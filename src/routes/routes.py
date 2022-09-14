import requests

from flask import Flask, request

from src.exceptions import FileHandlingException
from src.constants import TIMEOUT, FILEPATH
from src.routes import BaseResponse

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


    num_of_messages = int(request.args.get('num', default=20))
    filter_keyword = request.args.get('filter')
    timeout = int(request.args.get('timeout', default=TIMEOUT))

    full_path = filepath + filename
    log_results = LogCollectionService.log_reader(full_path, num_of_messages, filter_keyword, timeout)

    return BaseResponse(results=log_results)


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
    results = requests.post(url=f"{data['url']}/listen", json=payload)
    return BaseResponse(results=results.json()['results'])


@app.route("/listen/", methods=["POST"])
def listen():
    """
    Listening port for the external server access
    """
    data = request.get_json()

    filename = data['filename']
    num_of_messages = data.get('num', 50)
    filter_keyword = data.get('filter')
    log_results = LogCollectionService.log_reader(filename, num_of_messages, filter_keyword)

    return BaseResponse(results=log_results)
