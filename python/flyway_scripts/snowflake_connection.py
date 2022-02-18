import os
import time
import logging
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

import config
import utils

conn_details = {
    'user': os.getenv('USER'),
    'account': os.getenv('ACCOUNT'),
    'password': os.getenv('PASSWORD'),
    'passphrase': os.getenv('PASSPHRASE'),
    #'private_key': os.getenv('PRIVATE_KEY', utils.read_txt('C:\\Users\\AndreaHrelja\\Projects\\Associated Bank\\snowflake-test-repo\\python\\flyway_scripts\\private_key.txt')),
    'private_key': os.getenv('PRIVATE_KEY')
}

p_key= serialization.load_pem_private_key(
    conn_details['private_key'].encode(),
    password=conn_details['passphrase'].encode(),
    backend=default_backend()
)

pkb = p_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

conn_details.update({'private_key': pkb})
logger = utils.get_logger(__file__)
logging.getLogger('snowflake.connector').setLevel(logging.WARNING)


def get_connection(conn_update=None):
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
                         "\nError message: {}".format(query, retry_num, retry_max, e))
            time.sleep(retry_num * retry_delay)
    
    cursor.close()
    connection.close()
    if result is None:
        return []
    return result


if __name__ == '__main__':
    conn = get_connection()
    cursor = conn.cursor()
    print(cursor.execute("SELECT 1").fetchall())