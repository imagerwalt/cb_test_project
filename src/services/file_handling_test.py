import pytest
from unittest import mock

from src.services.file_handling import FileHandlingService
from src.exceptions import FileHandlingException


@mock.patch('os.access', return_value=True)
@mock.patch('mimetypes.guess_type', return_value=('text/plain', None))
@mock.patch('os.path.isfile', return_value=True)
def test_verify_file_success(mock_isfile, mock_filetype, mock_os_access):
    filename = 'testfile.log'
    filepath = 'some/random/path'
    try:
        FileHandlingService.verify_file(filename, filepath)
    except FileHandlingException as exc:
        assert False


def test_verify_file_no_file_included():
    filename = None
    filepath = 'some/random/path'
    with pytest.raises(FileHandlingException):
        FileHandlingService.verify_file(filename, filepath)


@mock.patch('os.path.isfile', return_value=False)
def test_verify_file_file_not_found(mock_isfile):
    filename = 'incorrect_file_name.log'
    filepath = 'some/random/path'
    with pytest.raises(FileHandlingException):
        FileHandlingService.verify_file(filename, filepath)


@mock.patch('mimetypes.guess_type', return_value=('application/pdf', None))
def test_verify_file_wrong_file_type(mock_filetype):
    filename = 'it_is_a.pdf'
    filepath = 'some/random/path'
    with pytest.raises(FileHandlingException):
        FileHandlingService.verify_file(filename, filepath)


@mock.patch('os.access', return_value=False)
def test_verify_file_permission_denied(mock_os_access):
    filename = 'super_secret.log'
    filepath = 'some/random/path'
    with pytest.raises(FileHandlingException):
        FileHandlingService.verify_file(filename, filepath)
