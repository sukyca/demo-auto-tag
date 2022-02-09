import backout_functions

database = 'EDP_CONSUMER'
schema = 'DW_PERSONETICS'
table_name = '"T_TRANSACTIONS"'
column_names = ['TEST_COLUMN2', 'TEST_COLUMN3']

backout_functions.undo_add_columns(
    database=database,
    schema=schema,
    table_name=table_name,
    column_names=column_names
)
