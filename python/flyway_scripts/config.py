import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
REPO_DIR = os.path.join(BASE_DIR, 'ab')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

FLYWAY_CONFIG_DIR = os.path.join(TEMP_DIR, 'config')
FLYWAY_FILESYSTEM_DIR = os.path.join(TEMP_DIR, 'sql')
FLYWAY_OUTPUT_DIR = os.path.join(TEMP_DIR, 'output')
