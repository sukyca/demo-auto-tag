import os
import re
import sys
import json
import pytz
import argparse
import datetime as dt

import config
import validate
from make_flyway import get_repo_schema_scripts
from snowflake_connection import execute_query


logger = config.get_logger(__file__)
DEPLOYMENT_DTTM_UTC = os.getenv('DEPLOYMENT_DTTM_UTC')
if DEPLOYMENT_DTTM_UTC is None:
    raise ValueError("Deployment DTTM is not set")
    
deployment_dttm_utc = dt.datetime.strptime(DEPLOYMENT_DTTM_UTC, '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC)

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
    commands_file_path = os.path.join(config.TEMP_DIR, command + '.sh')
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
            'Invalid Migrations': []
        }
        
        for invalid_migration in command_output.get('invalidMigrations'):
            versioned_file_name = os.path.split(invalid_migration['filepath'])[1]
            default_file_name = versioned_file_name[0] + '{}__' + versioned_file_name.split('__')[1]
            error_info['Invalid Migrations'].append({
                'Versioned File Name': versioned_file_name,
                'Repository File Name': default_file_name,
                'File Path': os.path.join(command_output.get('database'), deserialized_command.get('schemas'), default_file_name),
                'Error Code': invalid_migration['errorDetails'].get('errorCode'),
                'Error Description': invalid_migration['errorDetails'].get('errorMessage')
            })
        
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
    query = """
    SELECT 
        "installed_rank", "version", "script", "success"
    FROM {}.{}."flyway_schema_history" 
    WHERE "installed_on" >= '{}'
    ORDER BY "success" DESC
    """
    migrations = []
    for db in repo_schema_scripts.keys():
        for schema in repo_schema_scripts[db].keys():
            results = execute_query(query.format(db, schema, deployment_dttm_utc))
            migrations.extend([
                {
                    'database': db,
                    'schema': schema,
                    'installed_rank': res[0],
                    'version': res[1],
                    'script': res[2],
                    'success': res[3]
                } for res in results
            ])
    return migrations


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


def run_flyway(command_name):
    if command_name == 'validate':
        commands = get_commands('validate')
        executed_successfully = execute_validate_commands(commands)
        if not executed_successfully:
            exit(1)
    
    elif command_name == 'migrate':
        commands = get_commands('migrate')
        executed_successfully = execute_migrate_commands(commands)
        if not executed_successfully:
            repo_schema_scripts, repo_backout_scripts = get_repo_schema_scripts()
            migrations = get_flyway_migrations(repo_schema_scripts)
            logger.error("The following migrations will be rolled back using the provided Python backout scripts:\n{}".format(json.dumps(migrations, indent=2)))
            exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run flyway commands')
    parser.add_argument('--validate', default=False, action='store_true', help='Run flyway --validate')
    parser.add_argument('--migrate', default=False, action='store_true', help='Run flyway --migrate')
    args = vars(parser.parse_args())
    #print(args)
    for command_name, execute in args.items():
        if execute:
            run_flyway(command_name)
    
