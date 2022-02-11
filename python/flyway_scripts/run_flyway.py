from distutils import command
import os
import re
import json
import pytz
import argparse
import datetime as dt

import utils
import config
import validate
from make_flyway import get_repo_schema_scripts
from snowflake_connection import execute_query


logger = utils.get_logger(__file__)
DEPLOYMENT_DTTM_UTC = os.getenv('DEPLOYMENT_DTTM_UTC', dt.datetime.now(pytz.UTC).strftime('%Y%m%d%H%M%S'))   
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
        
        for i, invalid_migration in enumerate(command_output.get('invalidMigrations')):
            versioned_file_name = os.path.split(invalid_migration['filepath'])[1]
            default_file_name = versioned_file_name[0] + '{}__' + versioned_file_name.split('__')[1]
            error_info['Invalid Migrations'].append({
                'Error #': i+1,
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
        print(json.dumps(command_output['error'], indent=2))
        file_name = re.search(validate.VERSIONED_DEPLOYED_MIGRATIONS, command_output['error'].get('message')).group()
        file_name = 'V{}__' + file_name.split('__')[1]
        backout_file_name = file_name.replace('V{}', 'backout{}').replace('.sql', '.py')
        error_info = {
            'Database': command_output.get('database'),
            'Schema': command_output.get('schemaName'),
            'File Name': file_name,
            'File Path': os.path.join(command_output.get('database'), command_output.get('schemaName'), file_name),
            'Backout File Name': backout_file_name,
            'Backout File Path': os.path.join(command_output.get('database'), command_output.get('schemaName'), backout_file_name),
            'Initial Schema Version': command_output.get('initialSchemaVersion'),
            'Error Code': command_output['error'].get('errorCode'),
            'Error Description': command_output['error'].get('message'),
        }
        if command_output.get('warnings'):
            error_info.update({'Warnings': command_output.get('warnings')})
        return error_info
    return None


def get_flyway_schema_migrations(repo_schema_scripts):
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
            results = execute_query(query.format(db, schema, deployment_dttm_utc), {'database': db, 'schema': schema})
            migrations.extend([
                {
                    'database': db,
                    'schema': schema,
                    'installed_rank': res[0],
                    'version': res[1],
                    'script': res[2],
                    'script_name': 'V{}__' + res[2].split('__')[1],
                    'success': res[3]
                } for res in results
            ])
    return migrations


def execute_validate_commands(commands, hide_command_output=False):
    deserialized_commands = []
    for command in commands:
        if hide_command_output:
            command += ' 1> /dev/null'
        os.system(command)
        deserialized_command = get_deserialized_command(command)
        deserialized_commands.append(deserialized_command)
    
    valid = True
    for deserialized_command in deserialized_commands:
        failed_validation = get_failed_validation_info(deserialized_command)
        if failed_validation:
            valid = False
            invalid_migrations = failed_validation.pop('Invalid Migrations')
            logger.info("`flyway {}` failed:\n{}".format('validate', json.dumps(failed_validation, indent=2)))
            for i, error in enumerate(invalid_migrations):
                logger.error("Error #{} Description:\n{}".format(i+1, error['Error Description']))
    return valid


def execute_migrate_commands(commands, hide_command_output=False):
    for command in commands:
        if hide_command_output:
            command += ' 1> /dev/null'
        os.system(command)
        deserialized_command = get_deserialized_command(command)
        failed_migration = get_failed_migration_info(deserialized_command)
        if failed_migration:
            error_description = failed_migration.pop('Error Description')
            logger.error("`flyway {}` failed:\n{}".format('migrate', json.dumps(failed_migration, indent=2)))
            logger.info("Error Description:\n{}".format(error_description))
            return False
    return True


def rollback_flyway():
    repo_schema_scripts, repo_backout_scripts = get_repo_schema_scripts()
    migrations = get_flyway_schema_migrations(repo_schema_scripts)
    
    logger.info("The following migrations will be rolled back using the provided Python backout scripts:\n{}".format(json.dumps(migrations, indent=2)))
    for migration in migrations[::-1]:
        db = migration['database']
        schema = migration['schema']
        rollback_command = 'python {}'.format(os.path.join(config.REPO_DIR, db, schema, repo_backout_scripts[db][schema][migration['script_name']]))
        
        logger.info("Rolling back `{}.{}` using {}".format(db, schema, rollback_command))
        rolled_back = os.system(rollback_command)
        if rolled_back == 1: # error
            pass # TODO
    
    for migration in migrations[::-1]:
        db = migration['database']
        schema = migration['schema']
        query = 'DELETE FROM {}.{}."flyway_schema_history" WHERE "installed_rank"={}'
        query = query.format(db, schema, migration['installed_rank'])
        
        execute_query(query, {'database': db, 'schema': schema})
        logger.info("Ran `{}` successfully".format(query))


def run_flyway(command_name):
    if command_name == 'validate':
        commands = get_commands('validate')
        executed_successfully = execute_validate_commands(commands, hide_command_output=True)
        if not executed_successfully:
            exit(1)
    
    elif command_name == 'migrate':
        commands = get_commands('migrate')
        executed_successfully = execute_migrate_commands(commands, hide_command_output=True)
        if not executed_successfully:
            rollback_flyway()
            exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run flyway commands')
    parser.add_argument('--validate', default=False, action='store_true', help='Run flyway --validate')
    parser.add_argument('--migrate', default=False, action='store_true', help='Run flyway --migrate')
    args = vars(parser.parse_args())
    
    _validate = args.pop('validate')
    _migrate = args.pop('migrate')
    
    if _validate:
        run_flyway('validate')
    elif _migrate:
        run_flyway('migrate')
    else:
        exit()

    
