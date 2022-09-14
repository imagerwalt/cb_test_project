Log Retrieving System
=====================
The log retrieving system is a simple REST API that allows users to quickly fetch the system log files without having to log on to individual machines.

The system returns results in reverse order, meaning the latest entries in the log will be presented first.

## Prerequisites
Python 3.8.9

## Installation and How to Start the App
To get started, you will need to set up a virtualenv:
```
cd cb_test_project
python3 -m venv venv
```
After that, please activate the virtualenv (venv):
```
source venv/bin/activate
```
You should then see (venv) prefix in the command prompt, that means you are currently in the virtualenv venv. After that, please install the dependencies (just the minimum requirements for Flask):
```
pip install -r requirements.txt
```
Finally, to start the app, please run:
```
flask --app src/routes/routes run
```
By default, the API will be running on `http://127.0.0.1:5000`

## How to Use

### REST API
The system is designed around one single endpoint -  `/read-logs`. There are a few GET parameters that a user can use to refine the log results:

PLEASE KEEP IN MIND THAT THE ENDPOINT `/read-logs/` (and other routes) ALWAYS ENDS WITH A TRAILING SLASH!! 

- `filename=system.log` - required
- `filepath=/var/log/` - optional - default: `/var/log/` if not specified (NOTE: Please include trailing slash)
- `num=500` - optional - default: 20 if not specified
- `filter=keyword` - optional - if specified, it will return only results with the keyword, the keyword is case-insensitive
- `timeout=60` - optional - default to 60 seconds. It will return a partial result list if the query exceeds the timeout limit

For example: a URL: `http://127.0.0.1:5000/read-logs/?filename=linux.log&num=250&filter=failure&filepath=/users/wlau/cb_test_project/&timeout=5` will return the most recent 250 results that contains the keyword "failure" from `/users/wlau/cb_test_project/linux.log`, with a timeout after 5 seconds

### Command Prompt (Bonus)
Alternatively, the system has a command prompt option that allows direct access to the log files without having to use go to the directory and run editor such as VIM to view the log files. To use that, simply run from the main directory:

Please note that the filename requires a fullpath (for example: `/var/log/system.log`)
```
python driver.py
```
This option also allows you to output the file to a specified location.

You can also run it the driver script with arguments. For example, if you want to get 25 logs with optional keyword "Statistic", you can run:
```
python driver.py /var/log/system.log 25 Statistic
```


## System Design Overview
This is a Python-based Flask system. It follows the standard MVC design paradigm, with `services` for the logics; and `routes` taking care of the traffic control as well as the API response.

### Route 
`src/routes/routes.py`

Route should be kept as simple as possible, with minimal logic in it. In the route function `read-logs`, it mostly just get all the GET arguments, then pass them to the service function.

### Services
#### LogCollectionService
LogCollectionService handles most of the logic for parsing and producing the data required for the results.

The logic of the log reader process is the read the log file in reverse, once it reads the `\n` character, it will yield the line, putting the line back to the original order(hence `[::-1]`), and store that in a generator which will be use for the further parsing. This can be run efficiently because it is reading the characters of the file bottom-up.

#### FileHandlingService
FileHandlingService has one single method `verify_file` in it to handle the file verification and exceptions.

### Other Files
- `constants.py` for storing constants
- `exceptions.py` for producing exceptions

## Extra Bonus
There are two other endpoints - `/external/` and `/listen/`. For fetching the logs from one server to another. The `/external/` is the request sender from the primary server, while the `/listen/` is the secondary server listening port.

Please keep in mind that this portion is done in a rather quick and dirty fashion, therefore it does not have as much tests with it. To run this test, we can set up a quick live demo with Ngrok and Postman.

## Todo
Security will be the most important thing, as the current setup, there is no authentications limiting access to the log file. We could add a decorator `@authtenticated` to the routes to add token-based access. 

Also, consider adding `@internal` to ensure some endpoints, such as `/listen/` is accessible only via URL or IP addresses that are whitelisted.

To make this log reader more useful, we should also add the date filters such as `start_time` and `end_time` to limit the results based on datetime. One potential challenge to it is that we have to ensure it works for different datetime formats. 
