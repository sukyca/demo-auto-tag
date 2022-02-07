from scripts.backout_scripts import backout_functions

backout_functions.undo_add_column(
    database='EDP_LANDING', 
    schema='LN_CICD_PIPELINE', 
    table_name='DUMMY_TABLE', 
    column_name='TEST_COLUMN'
)