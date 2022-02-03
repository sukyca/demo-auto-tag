
def clean_script_name(script_name):
    if script_name == '<< Flyway Baseline >>':
        return None
    else:
        return script_name.split('__')[1]

def clean_schema_scripts(schema_scripts):
    clean_schema_names = {}
    for db in schema_scripts.keys():
        clean_schema_names[db] = {}
        for schema_name in schema_scripts[db].keys():
            clean_schema_names[db][schema_name] = set()
            for script_name in schema_scripts[db][schema_name]:
                if script_name.startswith('V'):
                    script_name = clean_script_name(script_name)
                clean_schema_names[db][schema_name].add(script_name)
    return clean_schema_names
    
def write_to_file(path, content):
    if isinstance(content, list):
        content = '\n'.join(content)
    with open(path, 'w') as f:
        f.write(content)
