import backout_functions

database = 'EDP_CONSUMER'
schema = 'DW_PERSONETICS'
table_name = '"T_TRANSACTIONS"'

backout_functions.undo_create_table(
    database=database,
    schema=schema,
    table_name=table_name
)
