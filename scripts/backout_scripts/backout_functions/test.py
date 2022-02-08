import backout_functions

database = 'EDP_LANDING'
schema = 'LN_CICD_PIPELINE'
table_name = 'DUMMY_TABLE'
column_name = 'TEST_COLUMN'
column_mapping = {
    'TEST_COLUMN': 'BOOLEAN',
}

# backout_functions.undo_add_column(
#     database=database,
#     schema=schema,
#     table_name=table_name,
#     column_name=column_name
# )

# backout_functions.undo_drop_column(
#     database=database,
#     schema=schema,
#     table_name=table_name,
#     column_mapping=column_mapping
# )

# backout_functions.undo_drop_table(
#     database=database,
#     schema=schema,
#     table_name=table_name
# )


# backout_functions.undo_create_table(
#     database=database,
#     schema=schema,
#     table_name='TEMPORARY_TABLE'
# )

backout_functions.restore_table(
    database=database,
    schema=schema,
    table_name='DUMMY_TABLE'
)