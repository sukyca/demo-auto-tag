import os
import time
import json

from snowflake_connection import execute_query
import config
import utils

logger = utils.get_logger(__file__)


class RepoFileSystem:
    def __init__(self, repo_dir):
        self.repo_dir = repo_dir
        self.repo_scripts = {}
        self.db_scripts = {}

        self.set_repo_scripts()
        self.set_db_scripts()
        
    
    def set_repo_scripts(self):
        for db in os.listdir(self.repo_dir):
            self.repo_scripts[db] = {}
            for schema in os.listdir(os.path.join(self.repo_dir, db)):
                self.repo_scripts[db][schema] = []
                for script_name in os.listdir(os.path.join(self.repo_dir, db, schema)):
                    if script_name.startswith('backout'):
                        script_type = 'backout'
                        clean_script_name = script_name.split('__')[1]
                    elif script_name.startswith('R'):
                        script_type = 'repeatable'
                        clean_script_name = script_name
                    elif script_name.startswith('V'):
                        script_type = 'versioned'
                        clean_script_name = script_name.split('__')[1]
                    else:
                        script_type = 'unknown'
                        clean_script_name = script_name
                        logger.warning('Encountered an invalid script type for file {}.{}.{}'.format(db, schema, script_name))
                    self.repo_scripts[db][schema].append({
                        'script_name': script_name, # script_name = V{}__TABLE_NAME.sql
                        'clean_script_name': clean_script_name, # clean_script_name = TABLE_NAME.sql
                        'script_type': script_type
                    })
        

    def get_flyway_db_scripts(self, database, schema):
        conn_update = {
            'database': database,
            'schema': schema
        }
        query = 'SELECT * FROM "flyway_schema_history"'
        results = execute_query(query, conn_update)
        script_names = [res[4] for res in results]
        return script_names


    def set_db_scripts(self):
        for db in self.repo_scripts.keys():
            self.db_scripts[db] = {}
            for schema in self.repo_scripts[db].keys():
                self.db_scripts[db][schema] = []
                for script_name in self.get_flyway_db_scripts(database=db, schema=schema):
                    if script_name.startswith('R'):
                        script_type = 'repeatable'
                        clean_script_name = script_name
                    elif script_name.startswith('V'):
                        script_type = 'versioned'
                        clean_script_name = script_name.split('__')[1]
                    else:
                        script_type = 'unknown'
                        clean_script_name = script_name
                        logger.warning('Encountered an invalid script type for file {}.{}.{}'.format(db, schema, script_name))
                    self.db_scripts[db][schema].append({
                        'script_name': script_name, # script_name = V2022.01.01.10.30.00.100__TABLE_NAME.sql
                        'clean_script_name': clean_script_name, # clean_script_name = TABLE_NAME.sql
                        'script_type': script_type
                    })


class FlywayFileSystem(RepoFileSystem):
    def __init__(self, repo_dir, flyway_dir):
        super().__init__(repo_dir)
        self.flyway_dir = flyway_dir
        self.deployed_scripts = {}
        self.to_deploy_scripts = {}
    
    def generate(self):
        self.set_deployment_scripts()
        self.scripts_to_deploy = self.get_scripts_to_deploy()
    
    def _rename_deployed_scripts(self, deployed, db_scripts):
        deployed_scripts = []
        for script_name in db_scripts:
            for file_name in deployed:
                if script_name.endswith(file_name):
                    deployed_scripts.append(script_name)
        return deployed_scripts


    def _rename_to_deploy_scripts(self, to_deploy):
        to_deploy_scripts = []
        for file_name in to_deploy:
            if file_name.startswith('R__'):
                to_deploy_scripts.append(file_name)
            else:
                to_deploy_scripts.append('V{}__' + file_name)
        return to_deploy_scripts
    
    
    def set_deployment_scripts(self):
        flatten_dictlist = lambda dictlist, colname: [dicti[colname] for dicti in dictlist]
        # new_scripts = {}
        #scripts_to_deploy = {}
        for db in self.repo_scripts.keys():
            self.deployed_scripts[db] = {}
            self.to_deploy_scripts[db] = {}
            # new_scripts[db] = {}
            #scripts_to_deploy[db] = {}
            for schema in self.repo_scripts[db].keys():
                self.deployed_scripts[db][schema] = []
                self.to_deploy_scripts[db][schema] = []
                
                versioned_scripts = filter(lambda x: x['script_type'] == 'versioned', self.repo_scripts[db][schema])
                repeatable_scripts = filter(lambda x: x['script_type'] == 'repeatable', self.repo_scripts[db][schema])
                
                repo_scripts_ = set(flatten_dictlist(versioned_scripts, 'clean_script_name'))
                db_scripts_   = set(flatten_dictlist(self.db_scripts[db][schema], 'clean_script_name'))
                
                deployed = self._rename_deployed_scripts(
                    repo_scripts_.intersection(db_scripts_), 
                    flatten_dictlist(self.db_scripts[db][schema], 'script_name')
                )
                to_deploy = self._rename_to_deploy_scripts(
                    repo_scripts_.difference(db_scripts_).union(
                        flatten_dictlist(repeatable_scripts, 'script_name')
                    )
                )
                
                self.to_deploy_scripts[db][schema].extend(utils._get_sorted_files(to_deploy))
                self.deployed_scripts[db][schema].extend(utils._get_sorted_files(deployed))
        
        logger.info("Scripts to deploy:\n{}".format(json.dumps(self.to_deploy_scripts, indent=4)))
        #return scripts_to_deploy
    
    def get_scripts_to_deploy(self):
        scripts_to_deploy = {}
        for db in self.repo_scripts.keys():
            scripts_to_deploy[db] = {}
            for schema in self.repo_scripts[db].keys():
                scripts_to_deploy[db][schema] = utils._get_sorted_files(
                    self.deployed_scripts[db][schema] 
                    + self.to_deploy_scripts[db][schema]
                )
        return scripts_to_deploy
                
        

def main():
    start = time.time()
    flyway_fs = FlywayFileSystem(config.REPO_DIR, config.FLYWAY_FILESYSTEM_DIR)
    flyway_fs.generate()
    print(json.dumps(flyway_fs.scripts_to_deploy, indent=2))
    end = time.time()
    print("Time elapsed: {}s".format(end-start))
    # repo_schema_scripts, repo_backout_scripts = get_repo_schema_scripts()
    
    # validate.validate_repo_scripts(repo_schema_scripts)
    
    # db_schema_scripts = get_db_schema_scripts(repo_schema_scripts)
    # scripts_to_deploy, new_scripts = get_scripts_to_deploy(repo_schema_scripts, db_schema_scripts)
    
    # validate.validate_backout_scripts(new_scripts, repo_backout_scripts)
    
    # generate_flyway_filesystem(scripts_to_deploy)
    # generate_flyway_config(scripts_to_deploy)
    # generate_flyway_commands(scripts_to_deploy, command='validate')
    # generate_flyway_commands(scripts_to_deploy, command='migrate')

main()