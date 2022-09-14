from flask import json, Response


class ResponseStatus(object):
    OK = 'ok'
    INVALID_REQUEST = 'invalid_request'
    BAD_REQUEST = 'bad_request'
    FILE_NOT_FOUND = 'file_not_found'
    MISSING_FILENAME_PARAMETER = 'missing_filename_parameter'
    INVALID_FILE_TYPE = 'invalid_file_type'
    PERMISSION_DENIED = 'permission_denied'
    BAD_GATEWAY = 'bad gateway'
    INTERNAL_SERVER_ERROR = 'internal_server_error'


class BaseResponse(Response):
    def __init__(self, http_status=200, status_code=ResponseStatus.OK, mimetype='application/json', **kwargs):
        kwargs['http_status'] = http_status
        kwargs['status_code'] = status_code
        response = json.dumps(kwargs)
        super(BaseResponse, self).__init__(response=response, status=http_status, mimetype=mimetype)
