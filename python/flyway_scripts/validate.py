import os
import re
import json
import urllib.parse

import utils
import config

logger = utils.get_logger(__file__)

VERSIONED_MIGRATIONS = r'^V\{\}__\d+(_([A-Z]{2}|[A-Z]{3})-\d+)?_[a-zA-Z0-9_]+\.sql$'
VERSIONED_MIGRATIONS_BACKOUT = r'^backout\{\}__\d+(_([A-Z]{2}|[A-Z]{3})-\d+)?_[a-zA-Z0-9_]+\.py$'
REPEATABLE_MIGRATIONS = r'^R__[a-zA-Z0-9_-]+\.sql$'

VERSIONED_DEPLOYED_MIGRATIONS = r'V[0-9.]+__\d+(_([A-Z]{2}|[A-Z]{3})-\d+)?_[a-zA-Z0-9_]+\.sql'


def validate_repo_scripts():
    for db in os.listdir(config.REPO_DIR):
        for schema in os.listdir(os.path.join(config.REPO_DIR, db)):
            for script_name in os.listdir(os.path.join(config.REPO_DIR, db, schema)):
                pattern = r'^$'
                if script_name.startswith('V') and script_name.endswith('.sql'):
                    pattern = VERSIONED_MIGRATIONS
                elif script_name.startswith('R') and script_name.endswith('.sql'):
                    pattern = REPEATABLE_MIGRATIONS
                elif script_name.startswith('backout') and script_name.endswith('.py'):
                    pattern = VERSIONED_MIGRATIONS_BACKOUT
                match = re.match(pattern, script_name)
                if match is None:
                    logger.error("InvalidScriptName: Script is located at '{path}'. Validation help: "
                        "https://regexr.com/?expression={pattern}&text={script_name}".format(
                            script_name=urllib.parse.quote_plus(script_name), pattern=urllib.parse.quote_plus(pattern), path=db + "." + schema_name
                    ))
                    exit(1)
    logger.info("Repository script names validation completed successfully")                    


def validate_backout_scripts(scripts_to_deploy, repo_backout_scripts):
    for db in scripts_to_deploy.keys():
        for schema in scripts_to_deploy[db].keys():
            for repo_script, db_script in scripts_to_deploy[db][schema].items():
                deploy_script = db_script
                
                if db_script is None:
                    deploy_script = repo_script.format('CURRENT_TIMESTAMP()')
                
                if repo_script.startswith('V'):
                    backout_script = 'backout{}__' + utils.clean_script_name(repo_script).replace('.sql', '.py')
                    print(json.dumps(repo_backout_scripts, indent=4))
                    logger.error("MissingBackoutScript: Script '{}' is missing its backout python script. "
                        "Please create a python backout script named '{}'".format(
                            os.path.join(db, schema, repo_script),
                            os.path.join(db, schema, backout_script),
                        )
                    )
                    exit(1)
    logger.info("Backout script names validation completed successfully")                    
                