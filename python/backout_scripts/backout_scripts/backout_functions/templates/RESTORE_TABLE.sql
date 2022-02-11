DROP TABLE {table_name};

ALTER TABLE {database}.{schema}.{table_name}_CLONE
RENAME TO {database}.{schema}.{table_name};