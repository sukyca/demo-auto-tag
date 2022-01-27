import os
import sys
import time
import json
import shutil
import snowflake.connector
import datetime as dt

import utils
import validate

from config import get_logger
from config import REPO_DIR
from config import TEMP_DIR
from config import FLYWAY_CONFIG_DIR
from config import FLYWAY_FILESYSTEM_DIR
from config import FLYWAY_OUTPUT_DIR

logger = get_logger()

conn_details = {
    'user': os.getenv('USER'),
    'password': os.getenv('PASSWORD'),
    'account': os.getenv('ACCOUNT'),
}

def get_deployed_flyway_scripts(database, schema):
    conn_details.update({
        'database': database,
        'schema': schema
    })
    conn = snowflake.connector.connect(**conn_details)
    cursor = conn.cursor()
    query = 'SELECT * FROM "flyway_schema_history"'
    try:
        cursor.execute(query)
    except snowflake.connector.errors.ProgrammingError:
        cursor.close()
        conn.close()
        logger.error("Snowflake query '{}' execution failed".format(query))
        return []

    results = [res[4] for res in cursor.fetchall()]
    cursor.close()
    conn.close()
    return results


def get_repo_schema_scripts():
    """Traverse all database/schema level folders in repo
    Example output:
    {
        'EDP_CONSUMER': {
            'DW_NCR': [list of files],
            'DW_NCRUA': [list of files]
        },
        'EDP_CONFIG': {
            'DW_CFN': [list of files],
            'DW_CG': [list of files],
        }
        ...
    }

    Returns:
        dict: Contains a dictionary for each schema with 
              a list of files in the repository schema level
    """
    repo_schema_scripts = {}
    for db in os.listdir(REPO_DIR):
        repo_schema_scripts[db] = {}
        for schema in os.listdir(os.path.join(REPO_DIR, db)):
            repo_schema_scripts[db][schema] = []
            for item in os.listdir(os.path.join(REPO_DIR, db, schema)):
                repo_schema_scripts[db][schema].append(item) # file_name = V{}__TABLE_NAME.sql
    return repo_schema_scripts


def get_db_schema_scripts(repo_schema_scripts):
    db_schema_scripts = {}
    for db in repo_schema_scripts.keys():
        db_schema_scripts[db] = {}
        for schema_name in repo_schema_scripts[db].keys():
            db_schema_scripts[db][schema_name] = []
            for script_name in get_deployed_flyway_scripts(database=db, schema=schema_name):
                db_schema_scripts[db][schema_name].append(script_name) # script_name = V2022.01.01.10.30.00.100__TABLE_NAME.sql
    return db_schema_scripts


def _rename_deployed_scripts(deployed, db_scripts):
    deployed_scripts = []
    for script_name in db_scripts:
        for file_name in deployed:
            if script_name.endswith(file_name):
                deployed_scripts.append(script_name)
    return deployed_scripts


def _rename_to_deploy_scripts(to_deploy):
    to_deploy_scripts = []
    for file_name in to_deploy:
        if file_name.startswith('R__'):
            to_deploy_scripts.append(file_name)
        else:
            to_deploy_scripts.append('V{}__' + file_name)
    return to_deploy_scripts


def _get_sorted_files(files):
    versioned_files = []
    repeatable_files = []
    for file_name in files:
        clean_file_name = utils.clean_script_name(file_name)
        if clean_file_name[0].isnumeric():
            file_order = int(clean_file_name.split("_")[0])
        else:
            file_order = 0
        
        content = {
            'file_name': file_name,
            'file_order': file_order
        }
        
        if file_name.startswith('V'):
            versioned_files.append(content)
        else:
            repeatable_files.append(content)
    sorted_v = sorted(versioned_files, key=lambda x: x['file_order'], reverse=False)
    sorted_r = sorted(repeatable_files, key=lambda x: x['file_order'], reverse=False)
    return [item['file_name'] for item in sorted_v] + [item['file_name'] for item in sorted_r]


def get_scripts_to_deploy(repo_schema_scripts, db_schema_scripts):
    clean_repo_scripts = utils.clean_schema_scripts(repo_schema_scripts)
    clean_db_scripts = utils.clean_schema_scripts(db_schema_scripts)
    
    new_scripts = {}
    scripts_to_deploy = {}
    for db in clean_repo_scripts.keys():
        new_scripts[db] = {}
        scripts_to_deploy[db] = {}
        for schema_name in clean_repo_scripts[db].keys():
            db_scripts   = clean_db_scripts[db][schema_name]
            repo_scripts = clean_repo_scripts[db][schema_name]
            
            deployed = _rename_deployed_scripts(repo_scripts.intersection(db_scripts), db_schema_scripts[db][schema_name])
            to_deploy = _rename_to_deploy_scripts(repo_scripts.difference(db_scripts))        
            new_scripts[db].update({schema_name: _get_sorted_files(to_deploy)})
            scripts_to_deploy[db][schema_name] = _get_sorted_files(deployed + to_deploy)
    
    logger.info("Scripts to deploy:\n{}".format(json.dumps(new_scripts, indent=4)))
    return scripts_to_deploy


def generate_flyway_filesystem(scripts_to_deploy):
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    
    if not os.path.exists(FLYWAY_FILESYSTEM_DIR):
        os.mkdir(FLYWAY_FILESYSTEM_DIR)
    
    flyway_filesystem = {}
    for db in scripts_to_deploy.keys():
        flyway_filesystem[db] = {}
        for schema_name in scripts_to_deploy[db].keys():
            flyway_filesystem[db][schema_name] = []
            for file_name in scripts_to_deploy[db][schema_name]:
                time.sleep(0.001)
                version = dt.datetime.utcnow().strftime('%Y.%m.%d.%H.%M.%S.%f')[:-3]
                if file_name.startswith('V'):
                    content = {
                        'original_file': 'V{}__' + utils.clean_script_name(file_name),
                        'new_file': file_name.format(version)
                    }
                else:
                    content = {
                        'original_file': file_name,
                        'new_file': file_name
                    }
                    
                flyway_filesystem[db][schema_name].append(content)
    
    for db in flyway_filesystem.keys():
        if not os.path.exists(os.path.join(FLYWAY_FILESYSTEM_DIR, db)):
            os.mkdir(os.path.join(FLYWAY_FILESYSTEM_DIR, db))
        
        for schema_name, files in flyway_filesystem[db].items():
            if not os.path.exists(os.path.join(FLYWAY_FILESYSTEM_DIR, db, schema_name)):
                os.mkdir(os.path.join(FLYWAY_FILESYSTEM_DIR, db, schema_name))

            for content in files:
                original_file = os.path.join(REPO_DIR, db, schema_name, content['original_file'])
                new_file = os.path.join(FLYWAY_FILESYSTEM_DIR, db, schema_name, content['new_file'])
                shutil.copyfile(original_file, new_file)
    
    logger.info("Generated Flyway filesystem:\n{}".format(json.dumps({
        db + '.' + schema_name: str(len(flyway_filesystem[db][schema_name])) + ' files' 
        for db in flyway_filesystem.keys() for schema_name in flyway_filesystem[db].keys()
    }, indent=4)))
    return flyway_filesystem


def generate_flyway_config(repo_schema_scripts):
    if not os.path.exists(FLYWAY_CONFIG_DIR):
        os.mkdir(FLYWAY_CONFIG_DIR)
    
    all_configurations = []
    configuration = [
        'flyway.user=${USER}',
        'flyway.password=${PASSWORD}',
        'flyway.baselineOnMigrate=true',
        'flyway.ignoreMissingMigrations=true',
        'flyway.ignorePendingMigrations=true',
        'flyway.cleanDisabled=true',
        'flyway.createSchemas=false',
        'flyway.validateMigrationNaming=true'
    ]
    
    for db in repo_schema_scripts.keys():
        config = ['flyway.url=jdbc:snowflake://${ACCOUNT}.snowflakecomputing.com/?db=' + db] + configuration
        for schema_name in repo_schema_scripts[db].keys():
            all_configurations.append(config + ['flyway.schemas={}'.format(schema_name)])
            utils.write_to_file(
                os.path.join(FLYWAY_CONFIG_DIR, '{}.{}.config'.format(db, schema_name)), 
                all_configurations[-1]
            )
    
    logger.info("Generated configuration @ {}:\n{}".format(FLYWAY_CONFIG_DIR, json.dumps(all_configurations, indent=4)))
    return configuration


def generate_flyway_commands(scripts_to_deploy, command):
    if not os.path.exists(FLYWAY_OUTPUT_DIR):
        os.mkdir(FLYWAY_OUTPUT_DIR)
    if not os.path.exists(os.path.join(FLYWAY_OUTPUT_DIR, command)):
        os.mkdir(os.path.join(FLYWAY_OUTPUT_DIR, command))
    
    migrate_cmds = []
    for db in scripts_to_deploy.keys():
        for schema_name in scripts_to_deploy[db].keys():
            location = 'filesystem://{}'.format(os.path.join(FLYWAY_FILESYSTEM_DIR, db, schema_name))
            config_file = os.path.join(FLYWAY_CONFIG_DIR, '{}.{}.config'.format(db, schema_name))
            output_file = os.path.join(FLYWAY_OUTPUT_DIR, command, '{}.{}.json'.format(db, schema_name))
            cmd = 'flyway -locations="{}" -configFiles="{}" -schemas={} -outputFile="{}" -outputType="json" {}'.format(
                location, config_file, schema_name, output_file, command
            )
            migrate_cmds.append(cmd)
    utils.write_to_file(os.path.join(TEMP_DIR, '{}.sh'.format(command)), migrate_cmds)
    logger.info("Generated {} commands:\n{}".format(command, json.dumps(migrate_cmds, indent=4)))
    return migrate_cmds


def make_flyway():
    repo_schema_scripts = get_repo_schema_scripts()
    
    logger.info("Validating repository script names")
    validate.validate_repo_scripts(repo_schema_scripts)
    logger.info("Validation completed successfully")
    
    db_schema_scripts = get_db_schema_scripts(repo_schema_scripts)
    scripts_to_deploy = get_scripts_to_deploy(repo_schema_scripts, db_schema_scripts)
    
    logger.info("Generating Flyway filesystem")
    generate_flyway_filesystem(scripts_to_deploy)
    
    logger.info("Generating Flyway config")
    generate_flyway_config(scripts_to_deploy)
    
    logger.info("Generating Flyway migrate/validate commands")
    generate_flyway_commands(scripts_to_deploy, command='validate')
    generate_flyway_commands(scripts_to_deploy, command='migrate')


if __name__ == '__main__':
    if '--debug' in sys.argv:
        conn_details = conn_details = {
            'user': 'ahrelja',
            'password': 'Iolap1go!',
            'account': 'kv94459.us-east-2.aws'
        }
    
    make_flyway()
