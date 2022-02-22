import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
REPO_DIR = os.path.join(BASE_DIR, 'EDP_SNOWFLAKE')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

FLYWAY_RSA_FILE = os.path.join(TEMP_DIR, 'rsa_key.p8')

FLYWAY_DEPLOYMENT_DIR = os.path.join(TEMP_DIR, 'deployment')
FLYWAY_DEPLOYMENT = {
    'config': os.path.join(FLYWAY_DEPLOYMENT_DIR, 'config'),
    'output': os.path.join(FLYWAY_DEPLOYMENT_DIR, 'output'),
    'filesystem': os.path.join(FLYWAY_DEPLOYMENT_DIR, 'filesystem')
}

FLYWAY_ROLLBACK_DIR = os.path.join(TEMP_DIR, 'rollback')
FLYWAY_ROLLBACK = {
    'config': os.path.join(FLYWAY_ROLLBACK_DIR, 'config'),
    'output': os.path.join(FLYWAY_ROLLBACK_DIR, 'output'),
    'filesystem': os.path.join(FLYWAY_ROLLBACK_DIR, 'filesystem')
}

FLYWAY_CONFIG = [
    # flyway.url configuration is handled by make_flyway.py
    # flyway.schemas configuration is handled by make_flyway.py
    'flyway.user=${USER}',
    # 'flyway.password=${PASSWORD}',
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