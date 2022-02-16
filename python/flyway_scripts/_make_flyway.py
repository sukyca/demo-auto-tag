import os
import json
import time
import shutil
import pytz
import datetime as dt
from snowflake_connection import execute_query

import config
import utils
import validate

logger = utils.get_logger(__file__)


def yield_script_items(db, schema, script_list):
    for script_name in script_list:
        if script_name.startswith('V'):
            script_type = 'versioned'
            _clean_script_name = utils.clean_script_name(script_name)
        elif script_name.startswith('backout'):
            script_type = 'backout'
            _clean_script_name = utils.clean_script_name(script_name)
        elif script_name.startswith('R'):
            script_type = 'repeatable'
            _clean_script_name = script_name
        else:
            script_type = 'unknown'
            logger.warning('Encountered an invalid script type for file {}.{}.{}'.format(db, schema, script_name))
        
        item = {
            'script_name': script_name, # script_name = V{}__TABLE_NAME.sql
            'script_type': script_type, # script_type = ('versioned', 'backout', 'repeatable')
            'clean_script_name': _clean_script_name # clean_script_name = TABLE_NAME.sql
        }
        yield item


def get_repo_schema_scripts():
    repo_schema_scripts = {}
    for db in os.listdir(config.REPO_DIR):
        repo_schema_scripts[db] = {}
        for schema in os.listdir(os.path.join(config.REPO_DIR, db)):
            repo_scripts = os.listdir(os.path.join(config.REPO_DIR, db, schema))
            repo_schema_scripts[db][schema] = yield_script_items(db, schema, repo_scripts)
    return repo_schema_scripts


def get_db_schema_scripts(repo_schema_scripts):
    def get_deployed_flyway_scripts(database, schema):
        conn_update = {
            'database': database,
            'schema': schema
        }
        query = 'SELECT "script" FROM "flyway_schema_history"'
        results = execute_query(query, conn_update)
        return [res[0] for res in results]
    
    db_schema_scripts = {}
    for db in repo_schema_scripts.keys():
        db_schema_scripts[db] = {}
        for schema in repo_schema_scripts[db].keys():
            deployed_flyway_scripts = get_deployed_flyway_scripts(database=db, schema=schema)
            db_schema_scripts[db][schema] = yield_script_items(db, schema, deployed_flyway_scripts)
    return db_schema_scripts


def get_scripts_to_deploy(repo_scripts, db_scripts):
    scripts_to_deploy = {}
    for db in repo_scripts.keys():
        scripts_to_deploy[db] = {}
        for schema in repo_scripts[db].keys():
            v_repo_script_items = {x['clean_script_name']: x for x in repo_scripts[db][schema] if x['script_type'] in ('versioned', 'repeatable')}
            v_db_script_items = {x['clean_script_name']: x for x in db_scripts[db][schema] if x['script_type'] == 'versioned'}
            
            v_repo_scripts = set(v_repo_script_items.keys())
            v_db_scripts = set(v_db_script_items.keys())

            deployed = v_repo_scripts.intersection(v_db_scripts)
            to_deploy = v_repo_scripts.difference(deployed)
            
            scripts_to_deploy[db][schema] = {}
            for script_name in deployed:
                scripts_to_deploy[db][schema].update({
                    v_repo_script_items[script_name]['script_name']: v_db_script_items[script_name]['script_name']
                })
            
            for script_name in to_deploy:
                scripts_to_deploy[db][schema].update({
                    v_repo_script_items[script_name]['script_name']: None
                })
                
    logger.info("Scripts to deploy:\n{}".format(json.dumps(scripts_to_deploy, indent=2)))
    return scripts_to_deploy


def generate_flyway_filesystem(scripts_to_deploy):
    utils.mkdir(config.TEMP_DIR)
    utils.mkdir(config.FLYWAY_FILESYSTEM_DIR)
    
    for db in scripts_to_deploy.keys():
        utils.mkdir(os.path.join(config.FLYWAY_FILESYSTEM_DIR, db))
        for schema in scripts_to_deploy[db].keys():
            utils.mkdir(os.path.join(config.FLYWAY_FILESYSTEM_DIR, db, schema))
            for repo_script, db_script in scripts_to_deploy[db][schema].items():
                deploy_script = db_script
                if db_script is None:
                    time.sleep(0.001)
                    version = dt.datetime.now(pytz.UTC).strftime('%Y.%m.%d.%H.%M.%S.%f')[:-3]
                    deploy_script = repo_script.format(version)
                
                original_file = os.path.join(config.REPO_DIR, db, schema, repo_script)
                new_file = os.path.join(config.FLYWAY_FILESYSTEM_DIR, db, schema, deploy_script)
                shutil.copyfile(original_file, new_file)
    
    logger.info("Flyway filesystem successfully generated:\n{}".format(json.dumps({
        db + '.' + schema: str(len(scripts_to_deploy[db][schema])) + ' files' 
        for db in scripts_to_deploy.keys() for schema in scripts_to_deploy[db].keys()
    }, indent=4)))


def generate_flyway_config(repo_schema_scripts):
    if not os.path.exists(config.FLYWAY_CONFIG_DIR):
        os.mkdir(config.FLYWAY_CONFIG_DIR)
    
    for db in repo_schema_scripts.keys():
        configuration = ['flyway.url=jdbc:snowflake://${ACCOUNT}.snowflakecomputing.com/?db=' + db] + config.FLYWAY_CONFIG
        for schema_name in repo_schema_scripts[db].keys():
            utils.write_to_file(
                os.path.join(config.FLYWAY_CONFIG_DIR, '{}.{}.config'.format(db, schema_name)), 
                configuration + ['flyway.schemas={}'.format(schema_name)]
            )
    logger.info("Flyway config successfully generated")


def generate_flyway_commands(scripts_to_deploy, command):
    if not os.path.exists(config.FLYWAY_OUTPUT_DIR):
        os.mkdir(config.FLYWAY_OUTPUT_DIR)
    if not os.path.exists(os.path.join(config.FLYWAY_OUTPUT_DIR, command)):
        os.mkdir(os.path.join(config.FLYWAY_OUTPUT_DIR, command))
    
    cmd_template = 'flyway -locations="{}" -configFiles="{}" -schemas={} -outputFile="{}" -outputType="json" {}'
    migrate_cmds = []
    for db in scripts_to_deploy.keys():
        for schema_name in scripts_to_deploy[db].keys():
            location = 'filesystem://{}'.format(os.path.join(config.FLYWAY_FILESYSTEM_DIR, db, schema_name))
            config_file = os.path.join(config.FLYWAY_CONFIG_DIR, '{}.{}.config'.format(db, schema_name))
            output_file = os.path.join(config.FLYWAY_OUTPUT_DIR, command, '{}.{}.json'.format(db, schema_name))
            
            migrate_cmds.append(cmd_template.format(
                location, config_file, schema_name, output_file, command, output_file
            ))
    
    utils.write_to_file(os.path.join(config.TEMP_DIR, '{}.sh'.format(command)), migrate_cmds)
    logger.info("Flyway migrate/validate commands successfully generated")


def main():
    start = time.time()
    repo_schema_scripts = get_repo_schema_scripts()
    
    validate.validate_repo_scripts()
    # validate.validate_backout_scripts(scripts_to_deploy, repo_backout_scripts)
    
    db_schema_scripts = get_db_schema_scripts(repo_schema_scripts)
    scripts_to_deploy = get_scripts_to_deploy(repo_schema_scripts, db_schema_scripts)
    
    generate_flyway_filesystem(scripts_to_deploy)
    generate_flyway_config(scripts_to_deploy)
    generate_flyway_commands(scripts_to_deploy, command='validate')
    generate_flyway_commands(scripts_to_deploy, command='migrate')
    
    end = time.time()
    print("Time elapsed: {}s".format(end-start))


if __name__ == '__main__':
    main()