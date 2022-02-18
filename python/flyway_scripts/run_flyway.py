from asyncio import subprocess
import os
import re
import json
import pytz
import argparse
import datetime as dt

import utils
import config
import validate
import make_flyway
from snowflake_connection import execute_query


logger = utils.get_logger(__file__)
DEPLOYMENT_DTTM_UTC = os.getenv('DEPLOYMENT_DTTM_UTC', dt.datetime.now(pytz.UTC).strftime('%Y%m%d%H%M%S'))
deployment_dttm_utc = dt.datetime.strptime(DEPLOYMENT_DTTM_UTC, '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC)


def get_commands(command):
    commands_file_path = os.path.join(config.TEMP_DIR, command + '.sh')
    with open(commands_file_path, 'r') as f:
        return f.readlines()


class FlywayCommand:
    def __init__(self, command_name, command_str):
        self.command_name = command_name
        self.command_str = command_str
        self.command_output = None
        
        self._locations = None
        self._config_files = None
        self._schemas = None
        self._output_file = None
        
        self.__initialize()
    
    def __initialize(self):
        command = self.command_str.split(' -')
        deserialize = {
            'locations': '_locations', 
            'configFiles': '_config_files', 
            'schemas': '_schemas', 
            'outputFile': '_output_file',
        }
        for cmd_attr_name, cls_attr_name in deserialize.items():
            for arg in command:
                if arg.startswith(cmd_attr_name):
                    arg_value = arg.replace(cmd_attr_name + '=', '')
                    setattr(self, cls_attr_name, arg_value.replace('\"', ''))
    
    def set_command_output(self):
        self.command_output = utils.read_json(self._output_file)

    def has_completed_successfully(self):
        raise NotImplemented('Use `FlywayValidateCommand` or `FlywayMigrateCommand` classes to use this method')
    
    def execute(self):
        raise NotImplemented('Use `FlywayValidateCommand` or `FlywayMigrateCommand` classes to use this method')


class FlywayValidateCommand(FlywayCommand):
    command_name = 'validate'
    
    def __init__(self, command_str):
        super().__init__(self.command_name, command_str)
    
    def set_command_output(self):
        super().set_command_output()
        self.error_info = {
            'Database': self.command_output['database'],
            'Schema': self._schemas,
            'Error Code': self.command_output['errorDetails']['errorCode'] if self.command_output['errorDetails'] is not None else None,
            'Error Description': self.command_output['errorDetails']['errorMessage'] if self.command_output['errorDetails'] is not None else None,
            'Invalid Migrations': []
        }
        if self.command_output.get('warnings'):
            self.error_info.update({'Warnings': self.command_output['warnings']})
    
    def has_completed_successfully(self):
        self.set_command_output()
        if self.command_output.get('validationSuccessful', False) == False:
            for i, invalid_migration in enumerate(self.command_output.get('invalidMigrations', [])):
                versioned_file_name = os.path.split(invalid_migration['filepath'])[1]
                default_file_name = versioned_file_name[0] + '{}__' + versioned_file_name.split('__')[1]
                self.error_info['Invalid Migrations'].append({
                    'Error #': i+1,
                    'Versioned File Name': versioned_file_name,
                    'Repository File Name': default_file_name,
                    'File Path': os.path.join(self.error_info['Database'], self.error_info['Schema'], default_file_name),
                    'Error Code': invalid_migration['errorDetails']['errorCode'],
                    'Error Description': invalid_migration['errorDetails']['errorMessage']
                })
            return False
        return True

    def execute(self, hide_command_output=False):
        command = self.command_str.strip()
        if hide_command_output:
            command += ' 1> /dev/null'
        os.system(command)
        
        if not self.has_completed_successfully():
            invalid_migrations = self.error_info.pop('Invalid Migrations')
            logger.info("`flyway {}` failed:\n{}".format(self.command_name, json.dumps(self.error_info, indent=2)))
            for i, invalid_migration in invalid_migrations:
                logger.error("Error #{} Description:\n{}".format(i+1, invalid_migration['Error Description']))
        return self.has_completed_successfully()


class FlywayMigrateCommand(FlywayCommand):
    command_name = 'migrate'
    
    def __init__(self, command_str):
        super().__init__(self.command_name, command_str)

    def set_command_output(self):
        super().set_command_output()
        self.error_info = {
            'Database': self.command_output.get('database'),
            'Schema': self._schemas,
            'Initial Schema Version': self.command_output.get('initialSchemaVersion'),
            'Error Code': self.command_output.get('error', {}).get('errorCode'),
            'Error Description': self.command_output.get('error', {}).get('message'),
        }
        if self.command_output.get('warnings'):
            self.error_info.update({'Warnings': self.command_output['warnings']})

    def has_completed_successfully(self):
        self.set_command_output()
        if self.command_output.get('success', False) == False:
            v_fn_exists = re.search(validate.VERSIONED_DEPLOYED_MIGRATIONS, self.command_output['error']['message'])
            if v_fn_exists:
                file_name = v_fn_exists.group()
                file_name = 'V{}__' + file_name.split('__')[1]
                backout_file_name = file_name.replace('V{}', 'backout{}').replace('.sql', '.py')
                self.error_info.update({
                    'File Name': file_name,
                    'File Path': os.path.join(self.error_info['Database'], self.error_info['Schema'], file_name),
                    'Backout File Name': backout_file_name,
                    'Backout File Path': os.path.join(self.error_info['Database'], self.error_info['Schema'], backout_file_name),
                })
            else:
                logger.warning("Encountered a non-versioned failed migration")
            return False
        return True

    def execute(self, hide_command_output=False):
        command = self.command_str.strip()
        if hide_command_output:
            command += ' 1> /dev/null'
        os.system(command)
        
        if not self.has_completed_successfully():
            error_description = self.error_info.pop('Error Description')
            logger.info("`flyway {}` failed:\n{}".format(self.command_name, json.dumps(self.error_info, indent=2)))
            logger.info("Error Description:\n{}".format(error_description))
        return self.has_completed_successfully()


class FlywayRollback:
    def __init__(self, scripts_to_deploy, scripts_to_backout):
        self.scripts_to_deploy = scripts_to_deploy
        self.scripts_to_backout = scripts_to_backout
        self.query = """
        SELECT 
            "installed_rank", "version", "script", "success"
        FROM {}.{}."flyway_schema_history" 
        WHERE "installed_on" >= '{}'
        ORDER BY "success" DESC
        """
        self.migrations = self.get_rollback_migrations()
    
    def get_rollback_migrations(self):
        rollback_migrations = []
        for db in self.scripts_to_deploy.keys():
            for schema in self.scripts_to_deploy[db].keys():
                results = execute_query(self.query.format(db, schema, deployment_dttm_utc), {'database': db, 'schema': schema})
                script_items = make_flyway.get_script_items(db, schema, [res[2] for res in results])
                for res, item in zip(results, script_items):
                    if item['script_type'] == 'versioned':
                        script_name = 'V{}__' + item['clean_script_name']
                        backout_script_repo_location = os.path.join(config.REPO_DIR, db, schema, self.scripts_to_backout[db][schema][script_name])
                    elif item['script_type'] == 'repeatable':
                        script_name = item['script_name']
                        backout_script_repo_location = None
                    
                    rollback_migrations.append({
                        'database': db,
                        'schema': schema,
                        'installed_rank': res[0],
                        'version': res[1],
                        'script': res[2],
                        'script_repo_location': os.path.join(config.REPO_DIR, db, schema, script_name),
                        'script_flyway_location': os.path.join(config.FLYWAY_FILESYSTEM_DIR, db, schema, script_name),
                        'backout_script_repo_location': backout_script_repo_location,
                        'script_type': item['script_type'],
                        'success': res[3]
                    })
        #logger.info(json.dumps(rollback_migrations, indent=2))
        return rollback_migrations[::-1]

    def execute(self):
        logger.info("The following migrations will be rolled back using the provided Python backout scripts:\n{}".format(json.dumps(self.migrations, indent=2)))
        for migration in self.migrations:
            db = migration['database']
            schema = migration['schema']
            
            if migration['script_type'] == 'versioned':
                rollback_command = 'python "{}"'.format(migration['backout_script_location'])
                
                logger.info("Rolling back `{}.{}` using {}".format(db, schema, rollback_command))
                rolled_back = os.system(rollback_command)
                if rolled_back == 1: # error
                    pass # TODO
            
            elif migration['script_type'] == 'repeatable':
                production_script_content = subprocess.run(
                    'git show production:{}'.format(migration['script_location']), 
                    capture_output=True, 
                    encoding='utf-8'
                )
                utils.write_to_file(migration['script_flyway_location'], production_script_content.stdout)
                logger.info("Wrote the following content to {}:\n{}".format(
                    migration['script_flyway_location'],
                    production_script_content.stdout
                ))
                
        
        for migration in self.migrations:
            db = migration['database']
            schema = migration['schema']
            query = 'DELETE FROM {}.{}."flyway_schema_history" WHERE "installed_rank"={}'
            query = query.format(db, schema, migration['installed_rank'])
            
            execute_query(query, {'database': db, 'schema': schema})
            logger.info("Ran `{}` successfully".format(query))        


def run_flyway(command_name):
    commands = get_commands(command_name)
    if command_name == 'validate':
        Command = FlywayValidateCommand
    elif command_name == 'migrate':
        Command = FlywayMigrateCommand
    
    executions = []
    for command in commands:        
        cmd = Command(command)
        success = cmd.execute(hide_command_output=False)
        executions.append(success)
        if not success and command_name == 'migrate':
            repo_schema_scripts = make_flyway.get_repo_schema_scripts()
            db_schema_scripts = make_flyway.get_db_schema_scripts(repo_schema_scripts, deployment_dttm_utc)
            scripts_to_deploy, scripts_to_backout = make_flyway.get_scripts_to_deploy(repo_schema_scripts, db_schema_scripts)
            rollback = FlywayRollback(scripts_to_deploy, scripts_to_backout)
            rollback.execute()
            exit(1)
        
    if command_name == 'validate' and any(item is False for item in executions):
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
        exit("Argument provided does not match any supported arguments (--validate, --migrate)")
