import os
import sys
import json

from config import get_logger
from config import TEMP_DIR
import validate

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


def get_failed_execution_info(deserialized_command):
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
                    'File Path': invalid_migration['filepath'],
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


def execute_validate_commands(commands):
    deserialized_commands = []
    for command in commands:
        os.system(command)
        deserialized_command = get_deserialized_command(command)
        deserialized_commands.append(deserialized_command)
    
    valid = True
    for deserialized_command in deserialized_commands:
        execution_info = get_failed_execution_info(deserialized_command)
        if execution_info is not None:
            valid = False
            logger.info("flyway {} failed:\n{}".format('validate', json.dumps(execution_info, indent=2)))
    return valid


def execute_migrate_commands(commands):
    for command in commands:
        os.system(command)
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
        exit(1)


if __name__ == '__main__':
    sys.argv.pop(0)
    validate.validate_run_flyway_args(sys.argv)
    command = sys.argv[0].replace('--', '')
    
    run_flyway(command)
    