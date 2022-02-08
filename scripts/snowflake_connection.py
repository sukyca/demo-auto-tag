import os
import logging
import snowflake.connector


# conn_details = {
#     'user': os.getenv('USER'),
#     'password': os.getenv('PASSWORD'),
#     'account': os.getenv('ACCOUNT'),
# }

conn_details = {
    'user': 'ahrelja',
    'password': 'Iolap1go!',
    'account': 'kv94459.us-east-2.aws',
}

logging.getLogger('snowflake.connector').setLevel(logging.WARNING)


def get_connection(conn_update=None):
    if conn_update:
        conn_details.update(conn_update)
    return snowflake.connector.connect(**conn_details)


def execute_query(conn_update, query):
    connection = get_connection(conn_update)
    cursor = connection.cursor()
    
    try:
        cursor.execute(query)
    except Exception as e:
        cursor.close()
        connection.close()
        print("Snowflake query '{}' execution failed.\nError message: {}".format(query, e))
        return []
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result
