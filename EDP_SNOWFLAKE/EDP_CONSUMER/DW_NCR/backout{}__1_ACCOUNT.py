import backout_functions

database = 'EDP_CONSUMER'
schema = 'DW_NCR'
table_name = '"ACCOUNT"'

backout_functions.undo_create_table(
    database=database,
    schema=schema,
    table_name=table_name
)
