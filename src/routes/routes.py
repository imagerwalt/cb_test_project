import requests

from flask import Flask, request, Response

from src.exceptions import FileHandlingException
from src.constants import TIMEOUT, FILEPATH
from src.routes import BaseResponse, ResponseStatus

from src.services.log_collection import LogCollectionService
from src.services.file_handling import FileHandlingService

app = Flask(__name__)


@app.route("/")
def hello():
    return BaseResponse(results="Success")


@app.route("/read-logs/")
def read_logs():
    filename = request.args.get('filename')
    filepath = request.args.get('filepath', default=FILEPATH)
    try:
        FileHandlingService.verify_file(filename, filepath)
    except FileHandlingException as e:
        err = e.args[0]
        return BaseResponse(http_status=err['http_status'], status_code=err['status_code'], error=err['message'])

    filter_keyword = request.args.get('filter')
    try:
        num_of_messages = int(request.args.get('num', default=20))
        timeout = int(request.args.get('timeout', default=TIMEOUT))
    except ValueError as e:
        return BaseResponse(http_status=400, status_code=ResponseStatus.INVALID_REQUEST, error='Invalid Request')

    full_path = filepath + filename

    return Response(generate(full_path, num_of_messages, filter_keyword, timeout), mimetype='application/json')


@app.route("/external/", methods=["POST"])
def external_server():
    """
    Bonus for accessing secondary (external) server from primary one
    """
    data = request.get_json()
    payload = {
        'filename': data['filename'],
        'num': data.get('num'),
        'filter': data.get('filter')
    }
    results = requests.post(url=f"{data['url']}/listen/", json=payload)
    return Response(results, mimetype='application/json')


@app.route("/listen/", methods=["POST"])
def listen():
    """
    Listening port for the external server access
    """
    data = request.get_json()

    filename = data['filename']
    num_of_messages = data.get('num', 50)
    filter_keyword = data.get('filter')

    return Response(generate(filename, num_of_messages, filter_keyword))


def generate(full_path, num_of_messages, filter_keyword, timeout=TIMEOUT):
    for result in LogCollectionService.log_reader(full_path, num_of_messages, filter_keyword, timeout):
        yield result