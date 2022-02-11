import json


class BackoutScriptException(Exception):
    def __init__(self, message=None, fn_name='undo_add_columns', **params):
        error_message = ''
        message = self.message if message is None else message
        params.update({'function_name': fn_name})
        error_message = '{}\n{}'.format(message, json.dumps(params, indent=2))
        super(BackoutScriptException, self).__init__(error_message)


class ColumnDoesNotExist(BackoutScriptException):
    message = 'The column that is trying to be deleted does not exist'


class ColumnExists(BackoutScriptException):
    message = 'The column that is trying to be created already exists'


class TableDoesNotExist(BackoutScriptException):
    message = 'The table that is trying to be deleted does not exist'


class TableExists(BackoutScriptException):
    message = 'The table that is trying to be created already exists'


class QueryExecutionFailure(BackoutScriptException):
    message = 'Query execution failed'


class OfflineExecution(BackoutScriptException):
    message = 'Offline query execution not allowed'


class RestoreFailure(BackoutScriptException):
    pass
