class FileHandlingException(Exception):
    def __init__(self, message=None, http_status=None, status_code=None, **kwargs):
        kwargs['message'] = message
        kwargs['status_code'] = status_code
        kwargs['http_status'] = http_status
        super(Exception, self).__init__(kwargs)
