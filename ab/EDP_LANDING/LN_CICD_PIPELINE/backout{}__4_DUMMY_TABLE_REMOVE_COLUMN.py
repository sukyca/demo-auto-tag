from scripts.backout_scripts import backout_functions

database = 'EDP_LANDING', 
schema = 'LN_CICD_PIPELINE', 
table_name = 'DUMMY_TABLE', 
column_name = 'TEST_COLUMN'


backout_functions.undo_drop_table(
    database=database,
    schema=schema,
    table_name=table_name
)
