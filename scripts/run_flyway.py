import os
import re
import sys
import json
import pytz
import logging
import datetime as dt
import snowflake.connector

from config import get_logger
from config import conn_details
from config import TEMP_DIR
from make_flyway import get_repo_schema_scripts
import validate

DEPLOYMENT_DTTM_UTC = os.getenv('DEPLOYMENT_DTTM_UTC', dt.datetime.now(pytz.UTC).timestamp())
logger = get_logger()


def get_deserialized_command(command):
    _command = command.split(" -")
    deserialize = ['locations', 'configFiles', 'schemas', 'outputFile']
    deserialized = {
        'locations': str,
        'configFiles': str,
        'schemas': str,
        'outputFile': str,
        'command_output': object
    }
    for key in deserialize:
        for arg in _command:
            if arg.startswith(key):
                deserialized[key] = arg.replace(key + '=', '')
                deserialized[key] = deserialized[key].replace('\"', '')
    deserialized['command_output'] = get_command_output(deserialized.get('outputFile'))
    return deserialized


def get_command_output(output_file):
    with open(output_file, 'r') as f:
        return json.load(f)


def get_commands(command='validate'):
    commands_file_path = os.path.join(TEMP_DIR, command + '.sh')
    with open(commands_file_path, 'r') as f:
        return f.readlines()


def get_failed_validation_info(deserialized_command):
    command_output = deserialized_command.get('command_output')
    if command_output.get('validationSuccessful', False) == False:
        error_info = {
            'Database': command_output.get('database'),
            'Schema': deserialized_command.get('schemas'),
            'Error Code': command_output['errorDetails'].get('errorCode'),
            'Error Description': command_output['errorDetails'].get('errorMessage'),
            'Invalid Migrations': [
                {
                    'File Name': os.path.split(invalid_migration['filepath'])[1],
                    'File Path': os.path.join('ab', command_output.get('database'), deserialized_command.get('schemas'), os.path.split(invalid_migration['filepath'])[1]),
                    'Error Code': invalid_migration['errorDetails'].get('errorCode'),
                    'Error Description': invalid_migration['errorDetails'].get('errorMessage')
                }
                for invalid_migration in command_output.get('invalidMigrations')
            ]
        }
        if command_output.get('warnings'):
            error_info.update({'Warnings': command_output.get('warnings')})
        return error_info
    return None


def get_failed_migration_info(deserialized_command):
    command_output = deserialized_command.get('command_output')
    if command_output.get('success', False) == False:
        file_name = re.search(validate.VERSIONED_DEPLOYED_MIGRATIONS, command_output['error'].get('message')).group()
        file_name = 'V{}__' + file_name.split('__')[1]
        error_info = {
            'Database': command_output.get('database'),
            'Schema': command_output.get('schemaName'),
            'File Name': file_name,
            'File Path': os.path.join('ab', command_output.get('database'), command_output.get('schemaName'), file_name),
            'Initial Schema Version': command_output.get('initialSchemaVersion'),
            'Error Code': command_output['error'].get('errorCode'),
            'Error Description': command_output['error'].get('message'),
        }
        if command_output.get('warnings'):
            error_info.update({'Warnings': command_output.get('warnings')})
        return error_info
    return None


def get_flyway_migrations(repo_schema_scripts):
    deployment_dttm_utc = dt.datetime.fromtimestamp(int(DEPLOYMENT_DTTM_UTC), pytz.UTC)
        
    successful_migrations = []
    failed_migrations = []
    
    conn = snowflake.connector.connect(**conn_details)
    cursor = conn.cursor()
    
    for db in repo_schema_scripts.keys():
        for schema in repo_schema_scripts[db].keys():
            query = """SELECT "version", "script", "success"
                FROM {}.{}."flyway_schema_history" 
                WHERE "installed_on" >= '{}'
                ORDER BY "success" DESC
            """.format(db, schema, deployment_dttm_utc)
            
            try:
                cursor.execute(query)
            except snowflake.connector.errors.ProgrammingError:
                cursor.close()
                conn.close()
                logger.error("Snowflake query '{}' execution failed".format(query))
                return []

            failed_migrations.extend([
                {
                    'version': res[0],
                    'script': res[1],
                    'success': res[2]
                } for res in cursor.fetchall() if res[2] == False
            ])
            successful_migrations.extend([
                {
                    'version': res[0],
                    'script': res[1],
                    'success': res[2]
                } for res in cursor.fetchall() if res[2] == True
            ])
    
    cursor.close()
    conn.close()
    return successful_migrations, failed_migrations


def execute_validate_commands(commands):
    deserialized_commands = []
    for command in commands:
        os.system(command)
        deserialized_command = get_deserialized_command(command)
        deserialized_commands.append(deserialized_command)
    
    valid = True
    for deserialized_command in deserialized_commands:
        failed_validation = get_failed_validation_info(deserialized_command)
        if failed_validation:
            valid = False
            logger.info("flyway {} failed:\n{}".format('validate', json.dumps(failed_validation, indent=2)))
            for i, error in enumerate(failed_validation['Invalid Migrations']):
                logger.error("Error {} Description:\n{}".format(i+1, error['Error Description']))
    return valid


def execute_migrate_commands(commands):
    for command in commands:
        os.system(command)
        deserialized_command = get_deserialized_command(command)
        failed_migration = get_failed_migration_info(deserialized_command)
        if failed_migration:
            logger.error("flyway {} failed:\n{}".format('migrate', json.dumps(failed_migration, indent=2)))
            logger.error("Error Description:\n{}".format(failed_migration['Error Description']))
            return False
    return True


def execute_commands(command_name, commands):
    if command_name == 'validate':
        return execute_validate_commands(commands)
    elif command_name == 'migrate':
        return execute_migrate_commands(commands)
    return False


def run_flyway(command_name):
    commands = get_commands(command_name)
    executed_successfully = execute_commands(command_name, commands)
    if not executed_successfully:
        repo_schema_scripts = get_repo_schema_scripts()
        successful_migrations, failed_migrations = get_flyway_migrations(repo_schema_scripts)
        logger.info("Successful migrations:\n{}".format(json.dumps(successful_migrations, indent=2)))
        logger.error("Failed migrations:\n{}".format(json.dumps(failed_migrations, indent=2)))
        exit(1)


if __name__ == '__main__':
    sys.argv.pop(0)
    validate.validate_run_flyway_args(sys.argv)
    command = sys.argv[0].replace('--', '')
    
    logging.getLogger('snowflake.connector').setLevel(logging.WARNING)
    run_flyway(command)
    