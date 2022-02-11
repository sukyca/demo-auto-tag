CREATE TABLE {table_name}_CLONE
CLONE {database}.{schema}.{table_name}
AT (TIMESTAMP => '{deployment_dttm_utc}'::TIMESTAMP);