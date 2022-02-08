import backout_functions

database = 'EDP_CONSUMER'
schema = 'DW_PERSONETICS'
table_name = '"T_TRANSACTIONS"'
column_names = ['TEST_COLUMN2', 'TEST_COLUMN3']
column_mapping = {
    column_name: 'BOOLEAN' for column_name in column_names
}


backout_functions.undo_drop_columns(
    database=database,
    schema=schema,
    table_name=table_name,
    column_mapping=column_mapping
)
