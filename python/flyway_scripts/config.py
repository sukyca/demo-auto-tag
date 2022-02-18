import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
REPO_DIR = os.path.join(BASE_DIR, 'EDP_SNOWFLAKE')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

FLYWAY_CONFIG_DIR = os.path.join(TEMP_DIR, 'config')
FLYWAY_FILESYSTEM_DIR = os.path.join(TEMP_DIR, 'sql')
FLYWAY_OUTPUT_DIR = os.path.join(TEMP_DIR, 'output')
FLYWAY_RSA_FILE = os.path.join(TEMP_DIR, 'rsa_key.p8')

FLYWAY_CONFIG = [
    # flyway.url configuration is handled by make_flyway.py
    # flyway.schemas configuration is handled by make_flyway.py
    'flyway.user=${USER}',
    'flyway.password=${PASSWORD}',
    'flyway.baselineOnMigrate=true',
    'flyway.ignoreMissingMigrations=true',
    'flyway.ignorePendingMigrations=true',
    'flyway.cleanDisabled=true',
    'flyway.createSchemas=false',
    'flyway.validateMigrationNaming=true'
]

SKIP_SCHEMAS = [
    'ADMIN'
]