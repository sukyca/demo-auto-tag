import os
import sys
import logging


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
REPO_DIR = os.path.join(BASE_DIR, 'ab')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

FLYWAY_CONFIG_DIR = os.path.join(TEMP_DIR, 'config')
FLYWAY_FILESYSTEM_DIR = os.path.join(TEMP_DIR, 'sql')
FLYWAY_OUTPUT_DIR = os.path.join(TEMP_DIR, 'output')

conn_details = {
    'user': os.getenv('USER'),
    'password': os.getenv('PASSWORD'),
    'account': os.getenv('ACCOUNT'),
}

def get_logger(**kwargs):
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s %(name)s - %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=logging.INFO,
        stream=sys.stdout,
        **kwargs
    )

    return logging.getLogger(os.getenv('ENVIRONMENT', __file__))
