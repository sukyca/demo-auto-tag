import os
import sys
import logging

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
ALLOWED_SQL_SCRIPTS = [
    # Create/Drop table
    'UNDO_CREATE_TABLE', 'UNDO_DROP_TABLE',
    # Add/Drop columns
    'UNDO_ADD_COLUMNS', 'UNDO_DROP_COLUMNS',
    # Revert CRUD changes
    'RESTORE_TABLE'
]


def get_sql_script(sql_script_name):
    script_name = sql_script_name.upper()
    if script_name not in ALLOWED_SQL_SCRIPTS:
        raise ValueError('Expected one of [{}], got {}'.format(",".join(ALLOWED_SQL_SCRIPTS), script_name))

    with open(os.path.join(TEMPLATES_DIR, script_name + '.sql'), 'r') as f:
        return f.read()


def get_logger(logger_name, **kwargs):
    logging.basicConfig(
        format='[%(levelname)s] %(name)s - %(message)s',
        #datefmt='%Y/%m/%d %H:%M:%S',
        level=logging.INFO,
        stream=sys.stdout,
        **kwargs
    )

    return logging.getLogger(logger_name)