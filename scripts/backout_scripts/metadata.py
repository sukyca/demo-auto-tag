from snowflake_connection import execute_query


def table_exists(database, schema, table_name):
    conn_update = {
        'database': database
    }

    query = """
    SELECT 
        *
    FROM {}.INFORMATION_SCHEMA.\"TABLES\" 
    WHERE TABLE_SCHEMA='{}' 
        AND TABLE_NAME='{}'
    """
    result = execute_query(conn_update, query.format(database, schema, table_name))
    return len(result) == 1


def column_exists(database, schema, table_name, column_name):
    conn_update = {
        'database': database
    }

    query = """
    SELECT 
        *
    FROM {}.INFORMATION_SCHEMA.\"COLUMNS\" 
    WHERE TABLE_SCHEMA='{}' 
        AND TABLE_NAME='{}' 
        AND COLUMN_NAME='{}'
    """
    result = execute_query(conn_update, query.format(database, schema, table_name, column_name))
    return len(result) == 1
