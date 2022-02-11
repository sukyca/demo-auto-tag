import os
import sys
import logging


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
ALLOWED_SQL_SCRIPTS = [
    # Create/Drop table
    'UNDO_CREATE_TABLE', 'UNDO_DROP_TABLE',
    # Add/Drop columns
    'UNDO_ADD_COLUMNS',
    # Time Travel scripts
    'RESTORE_TABLE', 'CLONE_TABLE'
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


def check_result_outcome(result, logger, error_message, success_message=None):
    if not success_message:
        success_message = "Query execution completed successfully"
    if result is not None:
        logger.info(success_message)
    else:
        logger.error(error_message)
