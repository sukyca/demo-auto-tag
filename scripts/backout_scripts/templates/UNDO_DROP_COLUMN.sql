-- Recreate the column
ALTER TABLE {database}.{schema}.{table_name}
ADD COLUMN {column_mapping};

-- Clone table to retrieve column data
CREATE TABLE {table_name}_CLONE
CLONE {database}.{schema}.{table_name}
AT (TIMESTAMP => '{deployment_dttm_utc}'::TIMESTAMP);

-- Drop current table without the dropped column
DROP TABLE {table_name};

-- Recreate the table
ALTER TABLE {database}.{schema}.{table_name}_CLONE
RENAME TO {database}.{schema}.{table_name};
