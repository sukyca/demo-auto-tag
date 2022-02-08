from . import utils
from .snowflake_connection import execute_query

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


def column_exists(database, schema, table_name, column_names):
    existing_columns_count = 0
    for column_name in column_names:
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
        existing_columns_count += len(result)
    return len(column_names) == existing_columns_count
