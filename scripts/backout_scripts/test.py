import backout_functions

table_name = 'DUMMY_TABLE'
column_name = 'description'
column_names = ['name', 'description']
column_mapping = {
    'id': 'INT NOT NULL DEFAULT 1',
    'name': 'VARCHAR NULL'
}


print('\nundo_create_table\n', backout_functions.undo_create_table(table_name))
print('\nundo_drop_table\n', backout_functions.undo_drop_table(table_name, column_mapping))
print('\nundo_add_column\n', backout_functions.undo_add_column(table_name, column_name))
print('\nundo_add_columns\n', backout_functions.undo_add_columns(table_name, column_names))
print('\nundo_drop_column\n', backout_functions.undo_drop_column(table_name, {'id': 'INT NOT NULL DEFAULT 1'}))
print('\nundo_drop_columns\n', backout_functions.undo_drop_columns(table_name, column_mapping))
