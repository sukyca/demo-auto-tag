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
    'flyway.password=${PASSWORD}',
    'flyway.baselineOnMigrate=true',
    'flyway.ignoreMissingMigrations=true',
    'flyway.ignorePendingMigrations=true',
    'flyway.cleanDisabled=true',
    'flyway.createSchemas=false',
    'flyway.validateMigrationNaming=true'
]

SKIP_SCHEMAS = {
    'ADMIN': [
        'NETWORK_POLICY'
    ],
    'EDP_CONFIG': [
        'CDL_ENGINE',
        'DBMGMT_FRAMEWORK',
        'EXTRACTION_FRAMEWORK',
        'INFORMATION_SCHEMA',
        'INGESTION_FRAMEWORK',
        'METADATA_MIRROR_FRAMEWORK',
        'PROMOTION_FRAMEWORK',
        'PUBLIC',
        'STREAMING_FRAMEWORK',
        'VALIDATION_FRAMEWORK',
    ],
    'EDP_CONFORM': [
        'CN_BLD',
        'CN_CONVERSION',
        'CN_CUSTOMER_360',
        'CN_ELC',
        'CN_INDIRECT_AUTO',
        'CN_PEPPLUS',
        'CN_RISK_ML',
        'CN_SIGNATURE',
        'CN_UOB',
        'CN_WEX',
        'INFORMATION_SCHEMA',
        'PUBLIC',
    ],
    'EDP_CONSUMER': [
        'DM_CUST_GROUP',
        'DM_DCI',
        'DM_FIN',
        'DM_PCIS',
        'DW',
        'DW_ABRC',
        'DW_AB_WEB',
        'DW_ACCTXREF',
        'DW_ACTIMIZE',
        'DW_AIS_OPS',
        'DW_AUDIT_SERVICES',
        'DW_BKOPS',
        'DW_BLD',
        'DW_CCPA',
        'DW_CI_STG',
        'DW_CLOUDCORDS',
        'DW_CMSI',
        'DW_CORPORATE_BANKING',
        'DW_CRA',
        'DW_CREDIT',
        'DW_CREDIT_RISK_ANALYTICS',
        'DW_CREDIT_RISK_REVIEW',
        'DW_CUSTOMER_360',
        'DW_CUSTOMER_CARE',
        'DW_DCI',
        'DW_ENT_SALESFORCE',
        'DW_ESB',
        'DW_FINANCE',
        'DW_FINANCE_IPM',
        'DW_FINASTRAGPP',
        'DW_FIN_ACCTG',
        'DW_G4S',
        'DW_HSA_TPA',
        'DW_INDIRECT_AUTO',
        'DW_INFORMENT',
        'DW_IPM_STG',
        'DW_IT_APPS_PROVISIONING',
        'DW_MARKETING',
        'DW_MARSHFIELD_CLINIC',
        'DW_MCO',
        'DW_MERGER',
        'DW_NAUTILUS',
        'DW_NCR',
        'DW_NFS',
        'DW_PAYMENTS',
        'DW_PERSONETICS',
        'DW_QRM',
        'DW_QRM_LS',
        'DW_RES_LENDING_SHARED',
        'DW_RETAIL_DELIVERY',
        'DW_RISK',
        'DW_SAM',
        'DW_SIGNATURE',
        'DW_STG',
        'DW_TEAMMATE',
        'DW_TIMETRADE',
        'DW_TRECS',
        'DW_UPSTART',
        'DW_WEALTH_MGMT',
        'DW_WIRES_OPS',
        'DW_XTIVA',
        'INFORMATION_SCHEMA',
        'PSA_INFORMENT',
        'PUBLIC',
    ],
    'EDP_LANDING': [
        'INFORMATION_SCHEMA',
        'LN_ACCUITY',
        'LN_ACTIMIZE',
        'LN_ACTIVE_DIRECTORY',
        'LN_AEGIS',
        'LN_ALLPRO',
        'LN_ANALYSIS',
        'LN_ARGO',
        'LN_ARMSYS',
        'LN_AUTO_FINANCE',
        'LN_AVAYA',
        'LN_BLACKBAUD',
        'LN_BLD',
        'LN_BNYM',
        'LN_CADENCE',
        'LN_CADENCE_MCO',
        'LN_CDMA',
        'LN_CHATHAM',
        'LN_CHECKFREE',
        'LN_CHECKS',
        'LN_CIBAR',
        #'LN_CICD_PIPELINE',
        'LN_CLOS',
        'LN_CMSI',
        'LN_COLLEAGUE_CONNECT',
        'LN_CORPINTEL',
        'LN_CORPINTEL_ARCHIVE',
        'LN_CORPRISKMANAGEMENT',
        'LN_CREDIT_RISK_REVIEW',
        'LN_CTR',
        'LN_CUSTOMER_CARE_REP',
        'LN_DCI',
        'LN_DEFI',
        'LN_DELUXE',
        'LN_DIALER',
        'LN_DRROIDS',
        'LN_DSE',
        'LN_DSTFANMAIL',
        'LN_DTPI',
        'LN_EARLY_WARNING',
        'LN_ELAN',
        'LN_EMANAGER',
        'LN_ENT_SALESFORCE',
        'LN_EPIC',
        'LN_EREFER',
        'LN_EVALUATE',
        'LN_FCDA',
        'LN_FDR',
        'LN_FINASTRA',
        'LN_FINASTRA_UOPEN',
        'LN_FINCEN',
        'LN_FISERVZELLETN',
        'LN_FISERV_COMO',
        'LN_FORTIGENT',
        'LN_FRAUD',
        'LN_FUNDATION',
        'LN_FX',
        'LN_GGBCF',
        'LN_GUARDIAN_ANALYTICS',
        'LN_HBAN_FDR',
        'LN_HBAN_HOGAN',
        'LN_IBMCAMPGNREP',
        'LN_IBM_PLANNING_ANALYTICS',
        'LN_ICPD',
        'LN_INFOLEASE',
        'LN_INFORMET_HIER',
        'LN_IOFFICE',
        'LN_IPIPELINE',
        'LN_ITSM',
        'LN_IVR',
        'LN_JCORE',
        'LN_JUNXURE',
        'LN_LAPTOPINFO',
        'LN_LENDINGPRO',
        'LN_LOOMIS',
        'LN_LQAS',
        'LN_MARITZCX',
        'LN_MBS',
        'LN_NAUTILUS',
        'LN_NELNET',
        'LN_NETSPEND',
        'LN_NFS',
        'LN_NUEDGE',
        'LN_ONLINE_BANKING',
        'LN_OPTADMIN',
        'LN_OPTRISK',
        'LN_ORIGENATE',
        'LN_PATHWAY',
        'LN_PAYCOR',
        'LN_PAYPLUS',
        'LN_PEPPLUS',
        'LN_PROSPCTNG_M',
        'LN_PROV_CREDIT',
        'LN_QRM',
        'LN_RATACOMPLY',
        'LN_REE',
        'LN_REF',
        'LN_RETAIL_OPS',
        'LN_SECURENOW',
        'LN_SERENGETI',
        'LN_SIGNATURE',
        'LN_SKIENCE',
        'LN_SMARTERPAY',
        'LN_SMARTSTREAM',
        'LN_SYSTRACK',
        'LN_TEAMMATE',
        'LN_TIMETRADE',
        'LN_TRIPOD',
        'LN_TRUST',
        'LN_UPSTART',
        'LN_VERINT',
        'LN_VISIONCONTENT',
        'LN_VISIONIP',
        'LN_WECARE',
        'LN_WEILAND',
        'LN_WEX',
        'LN_WEX_COBRA',
        'LN_WIRES_OPS',
        'LN_WMIS',
        'LN_XTIVA',
        'LN_YOURCAUSE',
        'LN_ZIPINFO',
        'PUBLIC',
    ]
}