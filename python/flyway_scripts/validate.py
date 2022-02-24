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
        filtered_schemas = filter(lambda x: x not in config.SKIP_SCHEMAS[db], os.listdir(os.path.join(config.REPO_DIR, db)))
        for schema in filtered_schemas:
            repo_scripts = filter(lambda x: x.endswith('.sql') or x.endswith('.py'), os.listdir(os.path.join(config.REPO_DIR, db, schema)))
            for script_name in repo_scripts:
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
                            path=db + "." + schema,
                            pattern=urllib.parse.quote_plus(pattern),
                            script_name=urllib.parse.quote_plus(script_name)
                    ))
                    exit(1)
    logger.info("Repository script names validation completed successfully")                    


def validate_backout_scripts(scripts_to_deploy, scripts_to_backout):
    for db in scripts_to_deploy.keys():
        for schema in scripts_to_deploy[db].keys():
            for repo_script, db_script in scripts_to_deploy[db][schema].items():
                if repo_script.startswith('V') and db_script is None and (
                    repo_script not in scripts_to_backout[db][schema].keys() or
                        repo_script in scripts_to_backout[db][schema].keys() 
                        and scripts_to_backout[db][schema][repo_script] is None
                    ):
                    print(json.dumps(scripts_to_backout, indent=4))
                    logger.error("MissingBackoutScript: Script '{}' is missing its backout python script. "
                        "Please create a python backout script named '{}'".format(
                            os.path.join(db, schema, repo_script),
                            os.path.join(db, schema, 'backout{}__' + utils.clean_script_name(repo_script)),
                        )
                    )
                    exit(1)
    logger.info("Backout script names validation completed successfully")                    
                