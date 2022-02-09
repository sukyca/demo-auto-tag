import sys
import logging


def get_logger(logger_name, **kwargs):
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s %(name)s - %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=logging.INFO,
        stream=sys.stdout,
        **kwargs
    )

    return logging.getLogger(logger_name)


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


def _rename_deployed_scripts(deployed, db_scripts):
    deployed_scripts = []
    for script_name in db_scripts:
        for file_name in deployed:
            if script_name.endswith(file_name):
                deployed_scripts.append(script_name)
    return deployed_scripts


def _rename_to_deploy_scripts(to_deploy):
    to_deploy_scripts = []
    for file_name in to_deploy:
        if file_name.startswith('R__'):
            to_deploy_scripts.append(file_name)
        else:
            to_deploy_scripts.append('V{}__' + file_name)
    return to_deploy_scripts


def _get_sorted_files(files):
    versioned_files = []
    repeatable_files = []
    for file_name in files:
        clean_file_name = clean_script_name(file_name)
        if clean_file_name[0].isnumeric():
            file_order = int(clean_file_name.split("_")[0])
        else:
            file_order = 0
        
        content = {
            'file_name': file_name,
            'file_order': file_order
        }
        
        if file_name.startswith('V'):
            versioned_files.append(content)
        else:
            repeatable_files.append(content)
    sorted_v = sorted(versioned_files, key=lambda x: x['file_order'], reverse=False)
    sorted_r = sorted(repeatable_files, key=lambda x: x['file_order'], reverse=False)
    return [item['file_name'] for item in sorted_v] + [item['file_name'] for item in sorted_r]


def write_to_file(path, content):
    if isinstance(content, list):
        content = '\n'.join(content)
    with open(path, 'w') as f:
        f.write(content)
