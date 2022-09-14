import mimetypes
import os.path

from src.exceptions import FileHandlingException
from src.routes import ResponseStatus


class FileHandlingService(object):
    @staticmethod
    def verify_file(filename, filepath):
        if not filename:
            err_message = "Please include a filename"
            status_code = ResponseStatus.MISSING_FILENAME_PARAMETER
            http_status = 400
            raise FileHandlingException(err_message, http_status=http_status, status_code=status_code)

        fullpath = filepath + filename
        if not os.path.isfile(fullpath):
            err_message = "File not found"
            status_code = ResponseStatus.FILE_NOT_FOUND
            http_status = 404
            raise FileHandlingException(err_message, http_status=http_status, status_code=status_code)

        file_type = mimetypes.guess_type(fullpath)
        if file_type != ('text/plain', None):
            err_message = "Invalid file type"
            status_code = ResponseStatus.INVALID_FILE_TYPE
            http_status = 400
            raise FileHandlingException(err_message, http_status=http_status, status_code=status_code)

        if not os.access(fullpath, os.R_OK):
            err_message = "You do not have the permission to read the file"
            status_code = ResponseStatus.PERMISSION_DENIED
            http_status = 400
            raise FileHandlingException(err_message, http_status=http_status, status_code=status_code)
