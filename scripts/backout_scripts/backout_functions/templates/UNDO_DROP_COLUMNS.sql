ALTER TABLE {database}.{schema}.{table_name}
ADD COLUMN {column_mapping};

CREATE TABLE {table_name}_CLONE
CLONE {database}.{schema}.{table_name}
AT (TIMESTAMP => '{deployment_dttm_utc}'::TIMESTAMP);

DROP TABLE {table_name};

ALTER TABLE {database}.{schema}.{table_name}_CLONE
RENAME TO {database}.{schema}.{table_name};