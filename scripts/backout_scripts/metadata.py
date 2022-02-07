import utils
from snowflake_connection import execute_query

logger = utils.get_logger(__file__)


def table_exists(database, schema, table_name):
    query = """
    SELECT 
        *
    FROM {database}.INFORMATION_SCHEMA.\"TABLES\" 
    WHERE TABLE_SCHEMA='{schema}' 
        AND TABLE_NAME='{table_name}'
    """.format(
        database=database,
        schema=schema,
        table_name=table_name
    )
    logger.info("Query resolved for table_exists function:\n{}".format(query))
    
    result = execute_query(query, {'database': database})
    if len(result) > 1:
        raise Exception("Query returned more than 1 record")
    return len(result) == 1


def column_exists(database, schema, table_name, column_name):
    query = """
    SELECT 
        *
    FROM {database}.INFORMATION_SCHEMA.\"COLUMNS\" 
    WHERE TABLE_SCHEMA='{schema}' 
        AND TABLE_NAME='{table_name}' 
        AND COLUMN_NAME='{column_name}'
    """.format(
        database=database,
        schema=schema,
        table_name=table_name,
        column_name=column_name
    )
    logger.info("Query resolved for table_exists function:\n{}".format(query))
    
    result = execute_query(query, {'database': database})
    if len(result) > 1:
        raise Exception("Query returned more than 1 record")    
    return len(result) == 1


def table_is_modified(database, schema, table_name, deployment_dttm_utc):
    current_sql = """
    SELECT COUNT(*) AS cnt
    FROM {database}.{schema}.{table_name}
    """.format(
        database=database,
        schema=schema,
        table_name=table_name
    )
    current_count = execute_query(current_sql, {'database': database, 'schema': schema})
    
    time_travel_sql = """
    SELECT COUNT(*) AS cnt
    FROM {database}.{schema}.{table_name} AT (TIMESTAMP => '{deployment_dttm_utc}'::TIMESTAMP)
    """.format(
        database=database,
        schema=schema,
        table_name=table_name,
        deployment_dttm_utc=deployment_dttm_utc
    )
    time_travel_count = execute_query(time_travel_sql, {'database': database, 'schema': schema})
    
    if current_count[0] != time_travel_count[0]:
        return True
    else:
        return False


def _get_table_column_names(database, schema, table_name):
    query = """
    SELECT 
        COLUMN_NAME
    FROM {database}.INFORMATION_SCHEMA.\"COLUMNS\" 
    WHERE TABLE_SCHEMA='{schema}' 
        AND TABLE_NAME='{table_name}'
    """.format(
        database=database,
        schema=schema,
        table_name=table_name
    )
    result = execute_query(query, {'database': database, 'schema': schema})
    if len(result) == 0:
        raise Exception("Query returned no records")    
    return [res[0] for res in result]