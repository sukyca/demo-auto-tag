import re

VERSIONED_MIGRATIONS = r'^V\{\}__\d+(_([A-Z]{2}|[A-Z]{3})-\d+)?_[a-zA-Z0-9_]+\.sql$'
REPEATABLE_MIGRATIONS = r'^R__[a-zA-Z0-9][a-zA-Z0-9_]+\.sql$'

class InvalidScriptName(Exception):
    pass

def validate_repo_scripts(repo_schema_scripts):
    for db in repo_schema_scripts.keys():
        for schema_name in repo_schema_scripts[db].keys():
            for file_name in repo_schema_scripts[db][schema_name]:
                pattern = r'^$'
                if file_name.startswith('V'):
                    pattern = VERSIONED_MIGRATIONS
                elif file_name.startswith('R'):
                    pattern = REPEATABLE_MIGRATIONS
                match = re.match(pattern, file_name)
                if match is None:
                    raise InvalidScriptName("Got '{}', validation ran using regex '{}'".format(file_name, pattern))
