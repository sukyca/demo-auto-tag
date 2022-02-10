import os
import time
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


def execute_query(query, conn_update=None, retry_max=3, retry_delay=3):
    connection = get_connection(conn_update)
    cursor = connection.cursor()
    result = None
    retry_num = 0
    
    while result is None and retry_num < retry_max:
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except Exception as e:
            retry_num += 1
            logger.error("Snowflake query '{}' execution failed. Trying again ({}/{})."
                         "\nError message: {}".format(query, retry_num+1, retry_max, e))
            time.sleep(retry_num * retry_delay)
    
    cursor.close()
    connection.close()
    return result
