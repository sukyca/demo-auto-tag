import os
import sys
import logging

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
ALLOWED_SQL_SCRIPTS = [
    'CREATE_TABLE', 'DROP_TABLE',
    'ADD_COLUMN', 'ADD_COLUMNS', 'DROP_COLUMN', 'DROP_COLUMNS',
    'INSERT_VALUES', 'DELETE_VALUES', 'UPDATE_VALUES'
]


def get_sql_script(sql_script_name):
    if sql_script_name.upper() not in ALLOWED_SQL_SCRIPTS:
        raise ValueError('Expected one of [{}], got {}'.format(",".join(ALLOWED_SQL_SCRIPTS), sql_script_name))

    with open(os.path.join(TEMPLATES_DIR, sql_script_name + '.sql'), 'r') as f:
        return f.read()


def get_logger(logger_name, **kwargs):
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s %(name)s - %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=logging.INFO,
        stream=sys.stdout,
        **kwargs
    )

    return logging.getLogger(logger_name)