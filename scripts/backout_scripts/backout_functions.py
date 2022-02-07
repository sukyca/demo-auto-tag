import os
import pytz
import datetime as dt

import metadata
from snowflake_connection import execute_query
from utils import get_sql_script
from utils import get_logger

logger = get_logger(__file__)
DEPLOYMENT_DTTM_UTC = os.getenv('DEPLOYMENT_DTTM_UTC')
if DEPLOYMENT_DTTM_UTC is None:
    raise ValueError("Deployment DTTM is not set")

deployment_dttm_utc = dt.datetime.fromtimestamp(DEPLOYMENT_DTTM_UTC, pytz.UTC)


def undo_create_table(database: str, schema: str, table_name: str):
    """undo_create_table

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): DROP TABLE {table_name}

    Returns:
        str: Drop Table script with populated placeholders
    """
    if metadata.table_exists(database, schema, table_name):
        conn_update = {
            'database': database,
            'schema': schema,
        }
        sql = get_sql_script('undo_create_table')
        query = sql.format(
            database=database,
            schema=schema,
            table_name=table_name
        )
        logger.info("Query resolved for undo_create_table function:\n{}".format(query))
        return execute_query(query, conn_update)
    else:
        raise


def undo_drop_table(database: str, schema: str, table_name: str):
    """undo_drop_table

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): UNDROP TABLE {table_name}

    Returns:
        str: Create Table script with populated placeholders
    """
    if not metadata.table_exists(database, schema, table_name):
        conn_update = {
            'database': database,
            'schema': schema,
        }
        sql = get_sql_script('undo_drop_table')
        query = sql.format(
            database=database,
            schema=schema,
            table_name=table_name
        )
        logger.info("Query resolved for undo_drop_table function:\n{}".format(query))
        return execute_query(query, conn_update)
    else:
        raise


def undo_add_column(database: str, schema: str, table_name: str, column_name: str):
    """undo_add_columns alias

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_name (str): DROP COLUMN {column_name}
    Returns:
        str: Alter Table script with populated placeholders
    """
    return undo_add_columns(database, schema, table_name, [column_name])


def undo_add_columns(database: str, schema: str, table_name: str, column_names: list):
    """undo_add_columns

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_names (list): DROP COLUMN {column_name}
    Returns:
        str: Alter Table script with populated placeholders
    """
    if metadata.column_exists(database, schema, table_name):
        conn_update = {
            'database': database,
            'schema': schema,
        }
        sql = get_sql_script('undo_add_columns')
        query = sql.format(
            database=database,
            schema=schema,
            table_name=table_name,
            column_names=",".join(column_names)
        )
        logger.info("Query resolved for undo_add_columns function:\n{}".format(query))
        return execute_query(query, conn_update)
    else:
        raise 


def undo_drop_column(database: str, schema: str, table_name: str, column_mapping: dict):
    """undo_drop_columns alias

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_mapping (dict): {column_name: column_type} mapping. 
            Example:
            {
                'person_id': 'INT NOT NULL DEFAULT 1'
            }

    Returns:
        str: Alter Table script with populated placeholders
    """
    if len(column_mapping) != 1:
        raise ValueError('Expected one column map, got {}'.format(len(column_mapping)))
    return undo_drop_columns(database, schema, table_name, column_mapping)
    

def undo_drop_columns(database: str, schema: str, table_name: str, column_mapping: dict):
    """undo_drop_columns

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_mapping (dict): {column_name: column_type} mapping. 
            Example:
            {
                'person_id': 'INT NOT NULL DEFAULT 1',
                'person_name': 'VARCHAR(100) NULL'
            }

    Returns:
        str: Alter Table script with populated placeholders
    """    
    if not metadata.column_exists(database, schema, table_name):
        conn_update = {
            'database': database,
            'schema': schema,
        }
        sql = get_sql_script('add_column')
        sql_body = ''
        for column_name, column_type in column_mapping.items():
            sql_body += '{} {},'.format(column_name, column_type)
        
        query = sql.format(
            database=database,
            schema=schema,
            table_name=table_name,
            column_mapping=sql_body[:-1],
            deployment_dttm_utc=deployment_dttm_utc
        )
        logger.info("Query resolved for undo_drop_columns function:\n{}".format(query))
        return execute_query(query, conn_update)
    else:
        raise 