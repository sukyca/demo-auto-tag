import backout_functions

database = 'EDP_CONSUMER'
schema = 'DW_NCR'
table_name = '"ACCOUNT"'
column_name = 'TEST_COLUMN'

backout_functions.undo_add_column(
    database=database,
    schema=schema,
    table_name=table_name,
    column_name=column_name
)
