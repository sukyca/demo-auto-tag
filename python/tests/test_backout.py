import time
import pytz
import datetime as dt

import backout_functions
from backout_functions import metadata
from backout_functions.snowflake_connection import execute_query


database = 'EDP_LANDING'
schema = 'LN_CICD_PIPELINE'
table_name = 'TEST_TABLE'
column_name = 'TEST_COLUMN'
column_names = ['TEST_COLUMN2', 'TEST_COLUMN3']

conn_update = {
    'database': database,
    'schema': schema
}


# def test_undo_create_table():
#     # create_table
#     execute_query('CREATE TABLE {} (id INT, _name VARCHAR, description VARCHAR)'.format(table_name), conn_update)
#     sql = backout_functions.utils.get_sql_script('undo_create_table')
#     query = sql.format(database=database, schema=schema, table_name=table_name)
#     execute_query(query, conn_update)
#     ## undo_create_table
#     backout_functions.undo_create_table(database=database, schema=schema, table_name=table_name)
#     assert metadata.table_exists(database, schema, table_name) == False


# def test_undo_drop_table():
#     if not metadata.table_exists(database, schema, table_name):
#         execute_query('CREATE TABLE {} (id INT, _name VARCHAR, description VARCHAR)'.format(table_name), conn_update)
    
#     # drop_table
#     execute_query('DROP TABLE {}'.format(table_name), conn_update)
#     sql = backout_functions.utils.get_sql_script('undo_drop_table')
#     query = sql.format(database=database, schema=schema, table_name=table_name)
#     execute_query(query, conn_update)
#     ## undo_drop_table
#     backout_functions.undo_drop_table(database=database, schema=schema, table_name=table_name)
#     assert metadata.table_exists(database, schema, table_name) == True


# def test_undo_add_column():
#     if not metadata.table_exists(database, schema, table_name):
#         execute_query('CREATE TABLE {} (id INT, _name VARCHAR, description VARCHAR)'.format(table_name), conn_update)
    
#     # add_column
#     execute_query('ALTER TABLE {} ADD {} BOOLEAN'.format(table_name, column_name), conn_update)
#     sql = backout_functions.utils.get_sql_script('undo_add_columns')
#     query = sql.format(database=database, schema=schema, table_name=table_name, column_names=column_name)
#     execute_query(query, conn_update)
#     ## undo_add_column
#     backout_functions.undo_add_column(database=database, schema=schema, table_name=table_name, column_name=column_name)
#     assert metadata.column_exists(database, schema, table_name, [column_name]) == False


# def test_undo_add_columns():
#     if not metadata.table_exists(database, schema, table_name):
#         execute_query('CREATE TABLE {} (id INT, _name VARCHAR, description VARCHAR)'.format(table_name), conn_update)
    
#     # add_columns
#     execute_query('ALTER TABLE {} ADD {} BOOLEAN, {} BOOLEAN'.format(table_name, *column_names), conn_update)
#     sql = backout_functions.utils.get_sql_script('undo_add_columns')
#     query = sql.format(database=database, schema=schema, table_name=table_name, column_names=column_names)
#     execute_query(query, conn_update)
#     ## undo_add_columns
#     backout_functions.undo_add_columns(database=database, schema=schema, table_name=table_name, column_names=column_names)
#     assert metadata.column_exists(database, schema, table_name, column_names) == False


def test_undo_drop_column():
    if metadata.table_exists(database, schema, table_name):
        execute_query('DROP TABLE {}'.format(table_name), conn_update)
    execute_query('CREATE TABLE {} (id INT, _name VARCHAR, description VARCHAR)'.format(table_name), conn_update)
    execute_query('COMMIT')
    #time.sleep(10)
    deployment_dttm_utc = dt.datetime.now(pytz.UTC)
    
    # drop_column
    column_name = '_name'
    execute_query('ALTER TABLE {} DROP COLUMN {}'.format(table_name, column_name), conn_update)
    
    sql = backout_functions.utils.get_sql_script('undo_drop_columns')
    queries = sql.format(database=database, schema=schema, table_name=table_name, column_names=column_name, deployment_dttm_utc=deployment_dttm_utc)
    for query in filter(None, queries.split(";")):
        execute_query(query, conn_update)
    ## undo_drop_column
    backout_functions.undo_drop_column(database=database, schema=schema, table_name=table_name, column_name=column_name)
    assert metadata.column_exists(database, schema, table_name, [column_name]) == True


# def test_undo_drop_columns():    
#     if metadata.table_exists(database, schema, table_name):
#         execute_query('DROP TABLE {}'.format(table_name), conn_update)
#     execute_query('CREATE TABLE {} (id INT, _name VARCHAR, description VARCHAR)'.format(table_name), conn_update)
#     time.sleep(3)
#     deployment_dttm_utc = dt.datetime.now(pytz.UTC)
    
#     # drop_columns
#     column_names = ['id', '_name']
#     execute_query('ALTER TABLE {} DROP COLUMN {}, {}'.format(table_name, *column_names), conn_update)
    
#     sql = backout_functions.utils.get_sql_script('undo_drop_columns')
#     queries = sql.format(database=database, schema=schema, table_name=table_name, column_names=column_names, deployment_dttm_utc=deployment_dttm_utc)
#     for query in filter(None, queries.split(";")):
#         execute_query(query, conn_update)
#     ## undo_drop_columns
#     backout_functions.undo_drop_columns(database=database, schema=schema, table_name=table_name, column_names=column_names)
#     assert metadata.column_exists(database, schema, table_name, column_names) == True
