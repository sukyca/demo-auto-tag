import os
import re
import json
import pytz
import argparse
import subprocess
import datetime as dt

import utils
import config
import validate
import make_flyway
from snowflake_connection import execute_query


logger = utils.get_logger(__file__)
ENVIRONMENT_NAME = os.getenv('ENVIRONMENT', 'development')
DEPLOYMENT_DTTM_UTC = os.getenv('DEPLOYMENT_DTTM_UTC', dt.datetime.now(pytz.UTC).strftime('%Y%m%d%H%M%S'))
deployment_dttm_utc = dt.datetime.strptime(DEPLOYMENT_DTTM_UTC, '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC)


def get_commands(command, rollback=False):
    flyway_dir = config.FLYWAY_DEPLOYMENT_DIR
    if rollback:
        flyway_dir = config.FLYWAY_ROLLBACK_DIR
    commands_file_path = os.path.join(flyway_dir, command + '.sh')
    with open(commands_file_path, 'r') as f:
        return f.readlines()


class FlywayCommand:
    def __init__(self, command_name, command_str, scripts_to_deploy, scripts_to_backout):
        self.scripts_to_deploy = scripts_to_deploy
        self.scripts_to_backout = scripts_to_backout
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
        self.__parse_config_file()

    def __parse_config_file(self):
        database = None
        schema = None
        configuration = utils.read_txt(self._config_files)
        for conf in configuration.split('\n'):
            if conf.startswith('flyway.url'):
                match = re.search(r'\?db=[A-Za-z0-9_]+', conf)
                if match is not None:
                    database = match.group().replace('?db=', '')
            elif conf.startswith('flyway.schemas'):
                schema = conf.replace('flyway.schemas=', '')
        self.database = database
        self.schema = schema

    def set_command_output(self):
        self.command_output = utils.read_json(self._output_file)

    def has_completed_successfully(self):
        raise NotImplemented('Use `FlywayValidateCommand` or `FlywayMigrateCommand` classes to use this method')
    
    def execute(self):
        raise NotImplemented('Use `FlywayValidateCommand` or `FlywayMigrateCommand` classes to use this method')


class FlywayValidateCommand(FlywayCommand):
    command_name = 'validate'
    
    def __init__(self, command_str, scripts_to_deploy, scripts_to_backout):
        super().__init__(self.command_name, command_str, scripts_to_deploy, scripts_to_backout)
    
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
            command += ' -q'
        
        logger.info("[EXECUTE CMD] Running `flyway validate`:\n{}".format(command))
        os.system(command)
        
        if not self.has_completed_successfully():
            invalid_migrations = self.error_info.pop('Invalid Migrations')
            logger.info("`flyway {}` failed:\n{}".format(self.command_name, json.dumps(self.error_info, indent=2)))
            for i, invalid_migration in enumerate(invalid_migrations):
                logger.error("Error #{} Description:\n{}".format(i+1, invalid_migration['Error Description']))
        return self.has_completed_successfully()


class FlywayMigrateCommand(FlywayCommand):
    command_name = 'migrate'
    
    def __init__(self, command_str, scripts_to_deploy, scripts_to_backout):
        super().__init__(self.command_name, command_str, scripts_to_deploy, scripts_to_backout)

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
            return False
        return True

    def execute(self, hide_command_output=False):
        command = self.command_str.strip()
        if hide_command_output:
            command += ' -q'
        
        script_items = make_flyway.get_script_items(
            self.database, self.schema,
            self.scripts_to_deploy[self.database][self.schema].keys()
        )

        conn_update = {'database': self.database, 'schema': self.schema}
        results = execute_query('SHOW EXTERNAL TABLES', conn_update)

        ext_tables = []
        custom_execution_types = ('repeatable_stg', 'repeatable_ff')
        for script_item in filter(lambda x: x['script_type'] in custom_execution_types, script_items):
            if script_item['script_type'] == 'repeatable_ff':
                logger.info("Found repeatable File Format - collecting External Table DDLs")
                filter_column = 10
                filter_name = '{}.{}.{}'.format(
                    self.database, self.schema,
                    script_item['clean_script_name'].lower().replace('r__ff_', ''))
                filter_name = filter_name.replace('.sql', '').upper()
            else: # repeatable_stg
                logger.info("Found repeatable Stage - collecting External Table DDLs")
                filter_column = 8
                filter_name = '@{}.{}.{}'.format(
                    self.database, self.schema,
                    script_item['clean_script_name'].lower().replace('r__stg_', ''))
                filter_name = filter_name.replace('.sql', '').upper()
            
            for result in filter(lambda x: x[filter_column] == filter_name, results):
                ext_table_name = result[1]
                ext_tables.append(ext_table_name)
        
        logger.info("[EXECUTE CMD] Running `flyway migrate`:\n{}".format(command))
        os.system(command)

        for ext_table_name in ext_tables:
            ext_table_ddl = execute_query('SELECT GET_DDL(\'table\', \'{}\')'.format(ext_table_name), conn_update)
            logger.info("[EXECUTE SQL] Recreating External Table: {}\n{}".format(ext_table_name, ext_table_ddl[0][0]))
            execute_query(ext_table_ddl[0][0], conn_update)
            
        if not self.has_completed_successfully():
            error_description = self.error_info.pop('Error Description')
            logger.info("`flyway {}` failed:\n{}".format(self.command_name, json.dumps(self.error_info, indent=2)))
            logger.error("Error Description:\n{}".format(error_description))
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
    
    def __fetch_previous_file_version(self, migration):
        utils.mkdir(os.path.join(config.FLYWAY_ROLLBACK['filesystem'], migration['database']))
        utils.mkdir(os.path.join(config.FLYWAY_ROLLBACK['filesystem'], migration['database'], migration['schema']))
        
        fetch_prod_cmd = 'git show {}~1:{}'.format(ENVIRONMENT_NAME, migration['script_repo_location'].replace('\\', '/'))
        logger.info("[EXECUTE CMD] Fetching previous file version: `{}`".format(fetch_prod_cmd))
        production_script_content = subprocess.run(fetch_prod_cmd, shell=True, capture_output=True, encoding='utf-8')
        utils.write_to_file(os.path.join(config.FLYWAY_ROLLBACK['filesystem'], migration['script_flyway_location']), production_script_content.stdout)
        
        logger.info("Wrote previous file version to {}:\n{}".format(
            os.path.join(config.FLYWAY_ROLLBACK['filesystem'], migration['script_flyway_location']),
            production_script_content.stdout
        ))
    
    def __execute_previous_file_version_rollback(self, scripts_to_rollback):
        make_flyway.generate_flyway_config(scripts_to_rollback, rollback=True)
        make_flyway.generate_flyway_commands(scripts_to_rollback, command='migrate', rollback=True)
        
        commands = get_commands('migrate', rollback=True)
        for command in commands:
            cmd = FlywayMigrateCommand(command)
            success = cmd.execute(hide_command_output=False)
            if not success:
                logger.warning('Flyway rollback failed for command `{}`'.format(command))        

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
                    else:
                        script_name = item['script_name']
                        backout_script_repo_location = None
                    
                    rollback_migrations.append({
                        'database': db,
                        'schema': schema,
                        'installed_rank': res[0],
                        'version': res[1],
                        'script': res[2],
                        'script_repo_location': os.path.join(os.path.basename(config.REPO_DIR), db, schema, script_name),
                        'script_flyway_location': os.path.join(db, schema, script_name),
                        'backout_script_repo_location': backout_script_repo_location,
                        'script_type': item['script_type'],
                        'success': res[3]
                    })
        #logger.info(json.dumps(rollback_migrations, indent=2))
        return rollback_migrations[::-1]

    def rollback_versioned_scripts(self, migrations):
        logger.info("The following migrations will be rolled back using the provided Python backout scripts:\n{}".format(json.dumps(self.migrations, indent=2)))
        for migration in migrations:
            # os.environ['DEPLOYMENT_DTTM_UTC'] = dt.datetime.now(pytz.UTC).strftime('%Y%m%d%H%M%S')
            db = migration['database']
            schema = migration['schema']
            rollback_command = 'python "{}"'.format(migration['backout_script_repo_location'])
            
            logger.info("Rolling back `{}.{}` using {}".format(db, schema, rollback_command))
            rolled_back = os.system(rollback_command)
            if rolled_back == 1: # error
                raise Exception("Versioned script rollback was not successful") # TODO
       
    def rollback_repeatable_scripts(self, migrations):
        scripts_to_rollback = {}
        for migration in migrations:
            db = migration['database']
            schema = migration['schema']
            if db not in scripts_to_rollback.keys():
                scripts_to_rollback[db] = {}
            if schema not in scripts_to_rollback[db].keys():
                scripts_to_rollback[db][schema] = {}
            self.__fetch_previous_file_version(migration)
        self.__execute_previous_file_version_rollback(scripts_to_rollback)

    def execute(self):
        versioned_migrations = filter(lambda x: x['script_type'] == 'versioned', self.migrations)
        repeatable_migrations = filter(lambda x: x['script_type'].startswith('repeatable'), self.migrations)
        
        self.rollback_versioned_scripts(versioned_migrations)
        
        for migration in self.migrations:
            db = migration['database']
            schema = migration['schema']
            query = 'DELETE FROM {}.{}."flyway_schema_history" WHERE "installed_rank"={}'
            query = query.format(db, schema, migration['installed_rank'])
            
            execute_query(query, {'database': db, 'schema': schema})
            logger.info("Ran `{}` successfully".format(query))

        self.rollback_repeatable_scripts(repeatable_migrations)


def run_flyway(command_name, hide_command_output=False):
    repo_schema_scripts = make_flyway.get_repo_schema_scripts()
    db_schema_scripts   = make_flyway.get_db_schema_scripts(repo_schema_scripts, deployment_dttm_utc)
    scripts_to_deploy, scripts_to_backout = make_flyway.get_scripts_to_deploy(repo_schema_scripts, db_schema_scripts)

    commands = get_commands(command_name)
    if command_name == 'validate':
        Command = FlywayValidateCommand
    elif command_name == 'migrate':
        Command = FlywayMigrateCommand
    
    executions = []
    for command in commands:
        cmd = Command(command, scripts_to_deploy, scripts_to_backout)
        success = cmd.execute(hide_command_output)
        executions.append(success)
        if not success and command_name == 'migrate':
            rollback = FlywayRollback(scripts_to_deploy, scripts_to_backout)
            rollback.execute()
            logger.warning("`flyway migrate` failed - changes rolled back. Please review deployment and try again.")
            exit(1)
        
    if command_name == 'validate' and any(item is False for item in executions):
        logger.warning("`flyway validate` failed. Please review deployment and try again.")
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run flyway commands')
    parser.add_argument('--validate', default=False, action='store_true', help='Run flyway --validate')
    parser.add_argument('--migrate', default=False, action='store_true', help='Run flyway --migrate')
    args = vars(parser.parse_args())
    
    _validate = args.pop('validate')
    _migrate = args.pop('migrate')
    
    if _validate:
        run_flyway('validate', hide_command_output=True)
    elif _migrate:
        run_flyway('migrate', hide_command_output=True)
    else:
        exit("Argument provided does not match any supported arguments (--validate, --migrate)")
    	
    logger.info("[DONE] Deployment completed successfully")