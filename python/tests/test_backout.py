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


def test_undo_create_table():
    # create_table
    _recreate_test_table()
    ## undo_create_table
    backout_functions.undo_create_table(database=database, schema=schema, table_name=table_name)
    assert metadata.table_exists(database, schema, table_name) == False


def test_undo_drop_table():
    _recreate_test_table()
    
    # drop_table
    execute_query('DROP TABLE {}'.format(table_name), conn_update)
    ## undo_drop_table
    backout_functions.undo_drop_table(database=database, schema=schema, table_name=table_name)
    assert metadata.table_exists(database, schema, table_name) == True


def test_undo_add_column():
    _recreate_test_table()
    
    # add_column
    execute_query('ALTER TABLE {} ADD {} BOOLEAN'.format(table_name, column_name), conn_update)
    ## undo_add_column
    backout_functions.undo_add_column(database=database, schema=schema, table_name=table_name, column_name=column_name)
    assert metadata.column_exists(database, schema, table_name, [column_name]) == False


def test_undo_add_columns():
    _recreate_test_table()
    
    # add_columns
    execute_query('ALTER TABLE {} ADD {} BOOLEAN, {} BOOLEAN'.format(table_name, *column_names), conn_update)
    ## undo_add_columns
    backout_functions.undo_add_columns(database=database, schema=schema, table_name=table_name, column_names=column_names)
    assert metadata.column_exists(database, schema, table_name, column_names) == False


def test_undo_drop_column():
    _recreate_test_table()
    
    # drop_column
    column_name = '_NAME'
    execute_query('ALTER TABLE {} DROP COLUMN {}'.format(table_name, column_name), conn_update)
    ## undo_drop_column
    backout_functions.undo_drop_column(database=database, schema=schema, table_name=table_name, column_name=column_name)
    assert metadata.column_exists(database, schema, table_name, [column_name]) == True


def test_undo_drop_columns():    
    _recreate_test_table()
    
    # drop_columns
    column_names = ['ID', '_NAME']
    execute_query('ALTER TABLE {} DROP COLUMN {}, {}'.format(table_name, *column_names), conn_update)
    ## undo_drop_columns
    backout_functions.undo_drop_columns(database=database, schema=schema, table_name=table_name, column_names=column_names)
    assert metadata.column_exists(database, schema, table_name, column_names) == True


def _recreate_test_table():
    if metadata.table_exists(database, schema, table_name):
        execute_query('DROP TABLE {}'.format(table_name), conn_update)
    execute_query('CREATE TABLE {} (ID INT, _NAME VARCHAR, description VARCHAR)'.format(table_name), conn_update)
    backout_functions.set_deployment_dttm_utc()