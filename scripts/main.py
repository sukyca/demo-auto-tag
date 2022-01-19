import os
import sys
import time
import json
import shutil
import logging
import psycopg2
import datetime as dt

import utils

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
REPO_DIR = os.path.join(BASE_DIR, 'ab')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

CONFIG_DIR = os.path.join(TEMP_DIR, 'config')
FLYWAY_FILESYSTEM_DIR = os.path.join(TEMP_DIR, 'sql')
FLYWAY_OUTPUT_DIR = os.path.join(TEMP_DIR, 'output')

logging.basicConfig(
    format='[%(levelname)s] %(asctime)s %(name)s - %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    stream=sys.stdout
)

logger = logging.getLogger(ENVIRONMENT)

conn_details = {
    'host': os.getenv('HOST'),
    'port': os.getenv('PORT'),
    'database': os.getenv('DATABASE'),
    'user': os.getenv('USER'),
    'password': os.getenv('PASSWORD'),
}


def get_deployed_flyway_scripts(schema):
    conn = psycopg2.connect(**conn_details)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM "{}".flyway_schema_history'.format(schema))
    except psycopg2.errors.UndefinedTable:
        cursor.close()
        conn.close()
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
                repo_schema_scripts[db][schema].append(item.replace('.sql', '')) # file_name = V{}__TABLE_NAME.sql
    return repo_schema_scripts

def get_db_schema_scripts(repo_schema_scripts):
    db_schema_scripts = {}
    for db in repo_schema_scripts.keys():
        db_schema_scripts[db] = {}
        for schema_name in repo_schema_scripts[db].keys():
            db_schema_scripts[db][schema_name] = []
            for script_name in get_deployed_flyway_scripts(schema=schema_name):
                db_schema_scripts[db][schema_name].append(script_name.replace('.sql', '')) # script_name = V2022.01.01.10.30.00.100__TABLE_NAME.sql
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
    non_versioned_files = []
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
            non_versioned_files.append(content)
    sorted_v = sorted(versioned_files, key=lambda x: x['file_order'], reverse=False)
    sorted_nonv = sorted(non_versioned_files, key=lambda x: x['file_order'], reverse=False)
    return [item['file_name'] for item in sorted_v] + [item['file_name'] for item in sorted_nonv]

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
                        'original_file': 'V{}__' + utils.clean_script_name(file_name) + '.sql',
                        'new_file': file_name.format(version) + '.sql'
                    }
                else:
                    content = {
                        'original_file': file_name + '.sql',
                        'new_file': file_name + '.sql'
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

def generate_flyway_config(repo_schema_scripts, environment='development'):
    if not os.path.exists(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)
    
    configuration = [
        'flyway.url=jdbc:postgresql://${HOST}:${PORT}/${DATABASE}',
        'flyway.user=${USER}',
        'flyway.password=${PASSWORD}',
        'flyway.baselineOnMigrate=true',
        'flyway.ignoreMissingMigrations=true',
        'flyway.cleanDisabled=true',
        'flyway.createSchemas=false',
        'flyway.validateMigrationNaming=true'
    ]
    
    for db in repo_schema_scripts.keys():
        for schema_name in repo_schema_scripts[db].keys():
            utils.write_to_file(
                os.path.join(CONFIG_DIR, '{}.{}.config'.format(environment, schema_name)), 
                configuration + ['flyway.schemas={}'.format(schema_name)]
            )
    
    logger.info("Generated configuration @ {}:\n{}".format(CONFIG_DIR, json.dumps(configuration, indent=4)))
    return configuration

def generate_flyway_commands(scripts_to_deploy, environment, command):
    if not os.path.exists(FLYWAY_OUTPUT_DIR):
        os.mkdir(FLYWAY_OUTPUT_DIR)
    
    migrate_cmds = ['OUTPUT_CODES=""']
    for db in scripts_to_deploy.keys():
        for schema_name in scripts_to_deploy[db].keys():
            location = 'filesystem://{}'.format(os.path.join(FLYWAY_FILESYSTEM_DIR, db, schema_name))
            config_file = os.path.join(CONFIG_DIR, '{}.{}.config'.format(environment, schema_name))
            output_file = os.path.join(FLYWAY_OUTPUT_DIR, '{}.{}.FlywayOutput.txt'.format(command, schema_name))
            utils.write_to_file(output_file, '')
            cmd = 'flyway -locations="{}" -configFiles="{}" -schemas={} -outputFile="{}" {} && OUTPUT_CODES="${OUTPUT_CODES} $?"'.format(
                location, config_file, schema_name, output_file, command
            )
            migrate_cmds.append(cmd)
    migrate_cmds += ['export OUTPUT_CODES']
    utils.write_to_file(os.path.join(TEMP_DIR, '{}.sh'.format(command)), migrate_cmds)
    logger.info("Generated {} commands:\n{}".format(command, json.dumps(migrate_cmds, indent=4)))
    return migrate_cmds


def main(environment):
    repo_schema_scripts = get_repo_schema_scripts()
    db_schema_scripts = get_db_schema_scripts(repo_schema_scripts)
    scripts_to_deploy = get_scripts_to_deploy(repo_schema_scripts, db_schema_scripts)
    
    logger.info("Generating Flyway filesystem")
    generate_flyway_filesystem(scripts_to_deploy)
    
    logger.info("Generating Flyway config")
    generate_flyway_config(repo_schema_scripts, environment)
    
    logger.info("Generating Flyway migrate/validate commands")
    generate_flyway_commands(repo_schema_scripts, environment, command='validate')
    generate_flyway_commands(repo_schema_scripts, environment, command='migrate')


if __name__ == '__main__':
    main(ENVIRONMENT)
