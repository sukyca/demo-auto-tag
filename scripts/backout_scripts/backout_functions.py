from utils import get_sql_script
import metadata


def undo_create_table(database, schema, table_name):
    """undo_create_table

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): DROP TABLE {table_name}

    Returns:
        str: Drop Table script with populated placeholders
    """
    if metadata.table_exists(database, schema, table_name):
        drop_table = get_sql_script('drop_table')
        return drop_table.format(table_name=table_name)


def undo_drop_table(database, schema, table_name, column_mapping):
    """undo_drop_table

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): CREATE TABLE {table_name}
        column_mapping (dict): {column_name: column_type} mapping. 
            Example:
            {
                'person_id': 'INT NOT NULL DEFAULT 1',
                'person_name': 'VARCHAR(100) NULL'
            }

    Returns:
        str: Create Table script with populated placeholders
    """
    create_table = get_sql_script('create_table')
    create_table_body = ''
    for column_name, column_type in column_mapping.items():
        create_table_body += '{} {},'.format(column_name, column_type)
    
    return create_table.format(
        table_name=table_name,
        column_mapping=create_table_body[:-1]
    )


def undo_add_column(database, schema, table_name, column_name):
    """undo_add_columns alias

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_name (str): DROP COLUMN {column_name}
    Returns:
        str: Alter Table script with populated placeholders
    """
    return undo_add_columns(table_name, [column_name])


def undo_add_columns(database, schema, table_name, column_names):
    """undo_add_columns

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_names (list): DROP COLUMN {column_name}
    Returns:
        str: Alter Table script with populated placeholders
    """
    drop_columns = get_sql_script('drop_columns')
    return drop_columns.format(
        table_name=table_name,
        column_names=",".join(column_names)
    )


def undo_drop_column(database, schema, table_name, column_mapping):
    """undo_drop_columns alias

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_mapping (dict): {column_name: column_type} mapping. 
            Example:
            {
                'person_id': 'INT NOT NULL DEFAULT 1'
            }

    Returns:
        str: Alter Table script with populated placeholders
    """
    if len(column_mapping) != 1:
        raise ValueError('Expected one column map, got {}'.format(len(column_mapping)))
    return undo_drop_columns(table_name, column_mapping)
    

def undo_drop_columns(database, schema, table_name, column_mapping):
    """undo_drop_columns

    Args:
        database (str): Database name
        schema (str): Schema name
        table_name (str): ALTER TABLE {table_name}
        column_mapping (dict): {column_name: column_type} mapping. 
            Example:
            {
                'person_id': 'INT NOT NULL DEFAULT 1',
                'person_name': 'VARCHAR(100) NULL'
            }

    Returns:
        str: Alter Table script with populated placeholders
    """
    add_column = get_sql_script('add_column')
    add_column_body = ''
    for column_name, column_type in column_mapping.items():
        add_column_body += '{} {},'.format(column_name, column_type)
    
    return add_column.format(
        table_name=table_name,
        column_mapping=add_column_body[:-1]
    )
