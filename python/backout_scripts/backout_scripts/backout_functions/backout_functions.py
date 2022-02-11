import os
import pytz
import datetime as dt

from .snowflake_connection import execute_query
from .utils import get_sql_script
from .utils import get_logger
from . import metadata
from . import errors
from . import utils

logger = get_logger(__file__)
DEPLOYMENT_DTTM_UTC = os.getenv('DEPLOYMENT_DTTM_UTC', dt.datetime.now(pytz.UTC).strftime('%Y%m%d%H%M%S'))
deployment_dttm_utc = dt.datetime.strptime(DEPLOYMENT_DTTM_UTC, '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC)


def undo_create_table(database: str, schema: str, table_name: str) -> None:
    """undo_create_table

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): DROP TABLE {table_name}

    Returns:
        str: Drop Table script with populated placeholders
    """
    logger.info("Running {}".format('undo_create_table'))
    if metadata.table_exists(database, schema, table_name):
        logger.info("Metadata `table_exists` check completed successfully")
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
        logger.info("Query resolved for undo_create_table function:\n\t{}\n".format(query))
        result = execute_query(query, conn_update)
        utils.check_result_outcome(result, logger, error_message=errors.QueryExecutionFailure(
            fn_name='undo_drop_columns', 
            database=database, 
            schema=schema, 
            table_name=table_name,
            query=query
        ))
    else:
        logger.error(errors.TableDoesNotExist(
            fn_name='undo_create_table', 
            database=database, 
            schema=schema, 
            table_name=table_name
        ))


def undo_drop_table(database: str, schema: str, table_name: str) -> None:
    """undo_drop_table

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): UNDROP TABLE {table_name}

    """
    logger.info("Running {}".format('undo_drop_table'))
    if not metadata.table_exists(database, schema, table_name):
        logger.info("Metadata check `table_exists` completed successfully")
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
        result = execute_query(query, conn_update)
        utils.check_result_outcome(result, logger, error_message=errors.QueryExecutionFailure(
            fn_name='undo_drop_columns', 
            database=database, 
            schema=schema, 
            table_name=table_name,
            query=query
        ))
    else:
        logger.error(errors.TableExists(
            fn_name='undo_drop_table', 
            database=database, 
            schema=schema, 
            table_name=table_name
        ))


def undo_add_column(database: str, schema: str, table_name: str, column_name: str) -> None:
    """undo_add_columns alias

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_name (str): DROP COLUMN {column_name}

    """
    return undo_add_columns(database, schema, table_name, [column_name])


def undo_add_columns(database: str, schema: str, table_name: str, column_names: list) -> None:
    """undo_add_columns

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_names (list): DROP COLUMN {column_name}

    """
    logger.info("Running {}".format('undo_add_columns'))
    if metadata.column_exists(database, schema, table_name, column_names):
        logger.info("Metadata check `column_exists` completed successfully")
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
        result = execute_query(query, conn_update)
        utils.check_result_outcome(result, logger, error_message=errors.QueryExecutionFailure(
            fn_name='undo_drop_columns', 
            database=database, 
            schema=schema, 
            table_name=table_name,
            query=query
        ))
    else:
        logger.error(errors.ColumnDoesNotExist(
            fn_name='undo_add_columns', 
            database=database, 
            schema=schema, 
            table_name=table_name,
            column_names=column_names
        ))


def undo_drop_column(database: str, schema: str, table_name: str, column_name: str) -> None:
    """undo_drop_columns alias

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_name (str): Column to recreate

    """
    return undo_drop_columns(database, schema, table_name, [column_name])
    

def undo_drop_columns(database: str, schema: str, table_name: str, column_names: list) -> None:
    """undo_drop_columns

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_names (list): List of column names to recreate

    """
    logger.info("Running {}".format('undo_drop_columns'))
    if not metadata.column_exists(database, schema, table_name, column_names):
        logger.info("Metadata check `column_exists` completed successfully")
        conn_update = {
            'database': database,
            'schema': schema,
        }
        sql = get_sql_script('undo_drop_columns')
        query = sql.format(
            database=database,
            schema=schema,
            table_name=table_name,
            deployment_dttm_utc=deployment_dttm_utc
        )
        queries = query.split(';')
        logger.info("Queries resolved for undo_drop_columns function:")
        for i, query in enumerate(filter(None, queries)):
            query = query.strip()
            logger.info("Query #{}:\n{}".format(i+1, query))
            result = execute_query(query, conn_update)
            utils.check_result_outcome(result, logger, error_message=errors.QueryExecutionFailure(
                fn_name='undo_drop_columns', 
                database=database, 
                schema=schema, 
                table_name=table_name,
                query=query
            ))
            
        if not metadata.table_exists(database, schema, table_name):
            query = "UNDROP TABLE {}".format(table_name)
            logger.info("Restore table failed. Running {}".format(query))
            result = execute_query(query, conn_update)
            utils.check_result_outcome(result, logger, 
                success_message=errors.RestoreFailure("Restore table failure: table `{}.{}.{}` is not restored".format(database, schema, table_name)),
                error_message=errors.QueryExecutionFailure(
                    fn_name='restore_table (undrop table handler)', 
                    database=database, 
                    schema=schema, 
                    table_name=table_name,
                    query=query
                )
            )
    else:
        logger.error(errors.ColumnExists(
            fn_name='undo_drop_columns', 
            database=database, 
            schema=schema, 
            table_name=table_name,
            column_names=column_names
        ))


def restore_table(database: str, schema: str, table_name: str, use_epoch_time=True) -> None:
    """restore_table

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): Table to restore
        use_epoch_time (bool, optional): use_epoch_time. Defaults to True.
    
    """
    logger.info("Running {}".format('restore_table'))
    if metadata.table_exists(database, schema, table_name):
        logger.info("Metadata `table_exists` check completed successfully")
        conn_update = {
            'database': database,
            'schema': schema,
        }
        sql = get_sql_script('restore_table')
        query = sql.format(
            database=database,
            schema=schema,
            table_name=table_name,
            deployment_dttm_utc=deployment_dttm_utc
        )
        queries = query.split(';')
        logger.info("Queries resolved for restore_table function:")
        for i, query in enumerate(filter(None, queries)):
            query = query.strip()
            logger.info("Query #{}:\n{}".format(i+1, query))
            result = execute_query(query, conn_update)
            utils.check_result_outcome(result, logger, error_message=errors.QueryExecutionFailure(
                fn_name='undo_drop_columns', 
                database=database, 
                schema=schema, 
                table_name=table_name,
                query=query
            ))
        
        if not metadata.table_exists(database, schema, table_name):
            query = "UNDROP TABLE {}".format(table_name)
            logger.info("Restore table failed. Running {}".format(query))
            result = execute_query(query, conn_update)
            utils.check_result_outcome(result, logger, 
                success_message=errors.RestoreFailure("Restore table failure: table `{}.{}.{}` is not restored".format(database, schema, table_name)),
                error_message=errors.QueryExecutionFailure(
                    fn_name='restore_table (undrop table handler)', 
                    database=database, 
                    schema=schema, 
                    table_name=table_name,
                    use_epoch_time=use_epoch_time,
                    query=query
                )
            )
    else:
        logger.error(errors.TableDoesNotExist(
            fn_name='restore_table', 
            database=database, 
            schema=schema, 
            table_name=table_name,
            use_epoch_time=use_epoch_time
        ))
