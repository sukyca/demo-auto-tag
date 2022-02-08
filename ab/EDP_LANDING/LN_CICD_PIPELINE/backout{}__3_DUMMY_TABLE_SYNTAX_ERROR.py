import backout_functions

database = 'EDP_LANDING'
schema = 'LN_CICD_PIPELINE'
table_name = 'DUMMY_TABLE'
column_name = 'TEST_COLUMN'
column_mapping = {
    column_name: 'BOOLEAN'
}


backout_functions.undo_drop_column(
    database=database,
    schema=schema,
    table_name=table_name,
    column_mapping=column_mapping
)
