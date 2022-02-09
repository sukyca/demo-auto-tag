import os
import time
import json
import shutil
import datetime as dt

import utils
import config
import validate
from snowflake_connection import execute_query


logger = utils.get_logger(__file__)


def get_deployed_flyway_scripts(database, schema):
    conn_update = {
        'database': database,
        'schema': schema
    }
    query = 'SELECT * FROM "flyway_schema_history"'
    results = execute_query(query, conn_update)
    script_names = [res[4] for res in results]
    return script_names


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
    repo_backout_scripts = {}
    for db in os.listdir(config.REPO_DIR):
        repo_schema_scripts[db] = {}
        repo_backout_scripts[db] = {}
        for schema in os.listdir(os.path.join(config.REPO_DIR, db)):
            repo_schema_scripts[db][schema] = []
            repo_backout_scripts[db][schema] = {}
            for file_name in os.listdir(os.path.join(config.REPO_DIR, db, schema)):
                if file_name.endswith('.sql'):
                    repo_schema_scripts[db][schema].append(file_name) # file_name = V{}__TABLE_NAME.sql
                elif file_name.endswith('.py'):
                    repo_backout_scripts[db][schema].update({
                        file_name.replace('backout', 'V').replace('.py', '.sql'): file_name # file_name = backout{}__TABLE_NAME.py
                    })
    return repo_schema_scripts, repo_backout_scripts


def get_db_schema_scripts(repo_schema_scripts):
    db_schema_scripts = {}
    for db in repo_schema_scripts.keys():
        db_schema_scripts[db] = {}
        for schema_name in repo_schema_scripts[db].keys():
            db_schema_scripts[db][schema_name] = []
            for script_name in get_deployed_flyway_scripts(database=db, schema=schema_name):
                db_schema_scripts[db][schema_name].append(script_name) # script_name = V2022.01.01.10.30.00.100__TABLE_NAME.sql
    return db_schema_scripts


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
            
            deployed = utils._rename_deployed_scripts(repo_scripts.intersection(db_scripts), db_schema_scripts[db][schema_name])
            to_deploy = utils._rename_to_deploy_scripts(repo_scripts.difference(db_scripts))        
            new_scripts[db].update({schema_name: utils._get_sorted_files(to_deploy)})
            scripts_to_deploy[db][schema_name] = utils._get_sorted_files(deployed + to_deploy)
    
    logger.info("Scripts to deploy:\n{}".format(json.dumps(new_scripts, indent=4)))
    return scripts_to_deploy, new_scripts


def generate_flyway_filesystem(scripts_to_deploy):
    if not os.path.exists(config.TEMP_DIR):
        os.mkdir(config.TEMP_DIR)
    
    if not os.path.exists(config.FLYWAY_FILESYSTEM_DIR):
        os.mkdir(config.FLYWAY_FILESYSTEM_DIR)
    
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
        if not os.path.exists(os.path.join(config.FLYWAY_FILESYSTEM_DIR, db)):
            os.mkdir(os.path.join(config.FLYWAY_FILESYSTEM_DIR, db))
        
        for schema_name, files in flyway_filesystem[db].items():
            if not os.path.exists(os.path.join(config.FLYWAY_FILESYSTEM_DIR, db, schema_name)):
                os.mkdir(os.path.join(config.FLYWAY_FILESYSTEM_DIR, db, schema_name))

            for content in files:
                original_file = os.path.join(config.REPO_DIR, db, schema_name, content['original_file'])
                new_file = os.path.join(config.FLYWAY_FILESYSTEM_DIR, db, schema_name, content['new_file'])
                shutil.copyfile(original_file, new_file)
    
    logger.info("Generated Flyway filesystem:\n{}".format(json.dumps({
        db + '.' + schema_name: str(len(flyway_filesystem[db][schema_name])) + ' files' 
        for db in flyway_filesystem.keys() for schema_name in flyway_filesystem[db].keys()
    }, indent=4)))


def generate_flyway_config(repo_schema_scripts):
    if not os.path.exists(config.FLYWAY_CONFIG_DIR):
        os.mkdir(config.FLYWAY_CONFIG_DIR)
    
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
        _configuration = ['flyway.url=jdbc:snowflake://${ACCOUNT}.snowflakecomputing.com/?db=' + db] + configuration
        for schema_name in repo_schema_scripts[db].keys():
            all_configurations.append(_configuration + ['flyway.schemas={}'.format(schema_name)])
            utils.write_to_file(
                os.path.join(config.FLYWAY_CONFIG_DIR, '{}.{}.config'.format(db, schema_name)), 
                all_configurations[-1]
            )


def generate_flyway_commands(scripts_to_deploy, command):
    if not os.path.exists(config.FLYWAY_OUTPUT_DIR):
        os.mkdir(config.FLYWAY_OUTPUT_DIR)
    if not os.path.exists(os.path.join(config.FLYWAY_OUTPUT_DIR, command)):
        os.mkdir(os.path.join(config.FLYWAY_OUTPUT_DIR, command))
    
    migrate_cmds = []
    for db in scripts_to_deploy.keys():
        for schema_name in scripts_to_deploy[db].keys():
            location = 'filesystem://{}'.format(os.path.join(config.FLYWAY_FILESYSTEM_DIR, db, schema_name))
            config_file = os.path.join(config.FLYWAY_CONFIG_DIR, '{}.{}.config'.format(db, schema_name))
            output_file = os.path.join(config.FLYWAY_OUTPUT_DIR, command, '{}.{}.json'.format(db, schema_name))
            cmd = 'flyway -locations="{}" -configFiles="{}" -schemas={} -outputFile="{}" -outputType="json" {}'.format(
                location, config_file, schema_name, output_file, command
            )
            migrate_cmds.append(cmd)
    
    utils.write_to_file(os.path.join(config.TEMP_DIR, '{}.sh'.format(command)), migrate_cmds)


def make_flyway():
    repo_schema_scripts, repo_backout_scripts = get_repo_schema_scripts()
    
    logger.info("Validating repository script names")
    validate.validate_repo_scripts(repo_schema_scripts)
    logger.info("Validation completed successfully")
    
    db_schema_scripts = get_db_schema_scripts(repo_schema_scripts)
    scripts_to_deploy, new_scripts = get_scripts_to_deploy(repo_schema_scripts, db_schema_scripts)
    
    logger.info("Validating backout scripts exist")
    validate.validate_backout_scripts(new_scripts, repo_backout_scripts)
    logger.info("Validation completed successfully")
    
    logger.info("Generating Flyway filesystem")
    generate_flyway_filesystem(scripts_to_deploy)
    logger.info("Flyway filesystem successfully generated")
    
    logger.info("Generating Flyway config")
    generate_flyway_config(scripts_to_deploy)
    logger.info("Flyway config successfully generated")
    
    logger.info("Generating Flyway migrate/validate commands")
    generate_flyway_commands(scripts_to_deploy, command='validate')
    generate_flyway_commands(scripts_to_deploy, command='migrate')
    logger.info("Flyway migrate/validate commands successfully generated")


if __name__ == '__main__':
    make_flyway()