import os
import logging
import snowflake.connector

from . import utils
from . import errors

conn_details = {
    'user': os.getenv('USER'),
    'password': os.getenv('PASSWORD'),
    'account': os.getenv('ACCOUNT'),
}
logger = utils.get_logger(__file__)

logging.getLogger('snowflake.connector').setLevel(logging.WARNING)


def get_connection(conn_update=None):
    if any(detail is None for detail in (conn_details.values())):
        raise errors.OfflineExecution
    if conn_update:
        conn_details.update(conn_update)
    return snowflake.connector.connect(**conn_details)


def execute_query(query, conn_update=None):
    connection = get_connection(conn_update)
    cursor = connection.cursor()
    
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except Exception as e:
        cursor.close()
        connection.close()
        
        logger.error("Snowflake query '{}' execution failed.\nError message: {}".format(query, e))
        return None
    
    cursor.close()
    connection.close()
    return result
