import os
import re
import json
import urllib.parse

import utils

logger = utils.get_logger(__file__)

VERSIONED_MIGRATIONS = r'^V\{\}__\d+(_([A-Z]{2}|[A-Z]{3})-\d+)?_[a-zA-Z0-9_]+\.sql$'
VERSIONED_MIGRATIONS_BACKOUT = r'^backout\{\}__\d+(_([A-Z]{2}|[A-Z]{3})-\d+)?_[a-zA-Z0-9_]+\.py$'
REPEATABLE_MIGRATIONS = r'^R__[a-zA-Z0-9][a-zA-Z0-9_]+\.sql$'

VERSIONED_DEPLOYED_MIGRATIONS = r'V[0-9.]+__\d+(_([A-Z]{2}|[A-Z]{3})-\d+)?_[a-zA-Z0-9_]+\.sql'


def validate_repo_scripts(repo_schema_scripts):
    for db in repo_schema_scripts.keys():
        for schema_name in repo_schema_scripts[db].keys():
            for file_name in repo_schema_scripts[db][schema_name]:
                pattern = r'^$'
                if file_name.startswith('V') and file_name.endswith('.sql'):
                    pattern = VERSIONED_MIGRATIONS
                elif file_name.startswith('R') and file_name.endswith('.sql'):
                    pattern = REPEATABLE_MIGRATIONS
                elif file_name.startswith('backout') and file_name.endswith('.py'):
                    pattern = VERSIONED_MIGRATIONS_BACKOUT
                match = re.match(pattern, file_name)
                if match is None:
                    logger.error("InvalidScriptName: Script is located at '{path}'. Validation help: "
                        "https://regexr.com/?expression={pattern}&text={script_name}".format(
                            script_name=urllib.parse.quote_plus(file_name), pattern=urllib.parse.quote_plus(pattern), path=db + "." + schema_name
                    ))
                    exit(1)


def validate_backout_scripts(new_scripts, repo_backout_scripts):
    for db in new_scripts.keys():
        for schema_name in new_scripts[db].keys():
            for versioned_file_name in new_scripts[db][schema_name]:
                default_file_name = versioned_file_name[0] + '{}__' + utils.clean_script_name(versioned_file_name)
                
                if default_file_name not in repo_backout_scripts[db][schema_name].keys():
                    backout_file_name = 'backout{}__' + utils.clean_script_name(versioned_file_name).replace('.sql', '.py')
                    print(json.dumps(repo_backout_scripts, indent=4))
                    logger.error("MissingBackoutScript: Script '{}' is missing its backout python script. "
                        "Please create a python backout script named '{}'".format(
                            os.path.join(db, schema_name, default_file_name),
                            os.path.join(db, schema_name, backout_file_name),
                        )
                    )
                    exit(1)
                