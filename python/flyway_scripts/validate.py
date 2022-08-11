import os
import re
import urllib.parse

import utils
import config

logger = utils.get_logger(__file__)

VERSIONED_MIGRATIONS = r'^V\{\}__\d+(_([A-Z]{2}|[A-Z]{3})-\d+)?_[a-zA-Z0-9_]+\.sql$'
VERSIONED_DEPLOYED_MIGRATIONS = r'V[0-9.]+__\d+(_([A-Z]{2}|[A-Z]{3})-\d+)?_[a-zA-Z0-9_]+\.sql'
VERSIONED_MIGRATIONS_BACKOUT = r'^backout\{\}__\d+(_([A-Z]{2}|[A-Z]{3})-\d+)?_[a-zA-Z0-9_]+\.py$'

REPEATABLE_MIGRATIONS = {
    'vw'    : r'^R__VW_[a-zA-Z0-9_-]+\.sql$',
    'sp'    : r'^R__SP_[a-zA-Z0-9_-]+\.sql$',
    'udf'   : r'^R__UDF_[a-zA-Z0-9_-]+\.sql$',
    'stg'   : r'^R__STG_[a-zA-Z0-9_-]+\.sql$',
    'ff'    : r'^R__FF_[a-zA-Z0-9_-]+\.sql$',
    'pp'    : r'^R__PP_[a-zA-Z0-9_-]+\.sql$',
    'ext'   : r'^R__EXT_[a-zA-Z0-9_-]+\.sql$',
    'mpol'  : r'^R__MPOL_[a-zA-Z0-9_-]+\.sql$',
    'rpol'  : r'^R__RPOL_[a-zA-Z0-9_-]+\.sql$',
    'tsk'   : r'^R__TSK_[a-zA-Z0-9_-]+\.sql$',
    'eudf'  : r'^R__EUDF_[a-zA-Z0-9_-]+\.sql$',
    'mvw'   : r'^R__MVW_[a-zA-Z0-9_-]+\.sql$',
    'seq'   : r'^R__SEQ_[a-zA-Z0-9_-]+\.sql$',
}


def validate_versioned_scripts():
    repo_dbs = os.listdir(config.REPO_DIR)
    for db in filter(lambda x: x not in config.SKIP_DATABASES, repo_dbs):
        repo_schemas = os.listdir(os.path.join(config.REPO_DIR, db))
        for schema in filter(lambda x: x not in config.SKIP_SCHEMAS.get(db, []), repo_schemas):
            schema_objs = os.listdir(os.path.join(config.REPO_DIR, db, schema))
            for script_name in filter(lambda x: (x.startswith('V') and x.endswith('.sql')) or (x.startswith('backout') and x.endswith('.py')), schema_objs):
                if script_name.startswith('V'):
                    pattern = VERSIONED_MIGRATIONS
                else:
                    pattern = VERSIONED_MIGRATIONS_BACKOUT
                match = re.match(pattern, script_name)
                if match is None:
                    logger.error("Invalid Versioned Script Name: '{path}'. Validation help: "
                        "https://regexr.com/?expression={pattern}&text={script_name}".format(
                            path=os.path.join(db, schema, script_name),
                            pattern=urllib.parse.quote_plus(pattern),
                            script_name=urllib.parse.quote_plus(script_name)
                    ))
                    exit(1)
    logger.info("Repository versioned script names validation completed successfully")                    


def validate_repeatable_scripts():
    repo_dbs = os.listdir(config.REPO_DIR)
    for db in filter(lambda x: x not in config.SKIP_DATABASES, repo_dbs):
        repo_schemas = os.listdir(os.path.join(config.REPO_DIR, db))
        for schema in filter(lambda x: x not in config.SKIP_SCHEMAS.get(db, []), repo_schemas):
            schema_objects = os.listdir(os.path.join(config.REPO_DIR, db, schema))
            for script_name in filter(lambda x: x.startswith('R') and x.endswith('.sql'), schema_objects):
                matches = []
                for _, pattern in REPEATABLE_MIGRATIONS.items():
                    match = re.match(pattern, script_name)
                    matches.append(match)
                if all(match is None for match in matches):
                    logger.error("Invalid Repeatable Script Name: '{path}'. Validation help: "
                        "https://regexr.com/?expression={pattern}&text={script_name}".format(
                            path=os.path.join(db, schema, script_name),
                            pattern=urllib.parse.quote_plus(pattern),
                            script_name=urllib.parse.quote_plus(script_name)
                    ))
                    exit(1)
    logger.info("Repository repeatable script names validation completed successfully")
    


def validate_backout_scripts(scripts_to_deploy, scripts_to_backout):
    for db in scripts_to_deploy.keys():
        for schema in scripts_to_deploy[db].keys():
            for repo_script, db_script in scripts_to_deploy[db][schema].items():
                if repo_script.startswith('V') and db_script is None and (
                    repo_script not in scripts_to_backout[db][schema].keys() or
                        repo_script in scripts_to_backout[db][schema].keys() 
                        and scripts_to_backout[db][schema][repo_script] is None
                    ):
                    logger.error("MissingBackoutScript: Script '{}' is missing its backout python script. "
                        "Please create a python backout script named '{}'".format(
                            os.path.join(db, schema, repo_script),
                            os.path.join(db, schema, 'backout{}__' + utils.clean_script_name(repo_script)),
                        )
                    )
                    exit(1)
    logger.info("Deployment backout script names validation completed successfully")                    
                