import backout_functions

database = 'EDP_CONSUMER'
schema = 'DW_PERSONETICS'
table_name = 'T_TRANSACTIONS'
column_name = 'TEST_COLUMN'

backout_functions.undo_drop_column(
    database=database,
    schema=schema,
    table_name=table_name,
    column_name=column_name
)
