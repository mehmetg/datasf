# DataSF Command Line Tool

Python module is a simple Socrata client to retrieve data from DataSF's api.

Currently it only implements the Mobile Food Schedule data retrieval.

## Requirements

* Python >= 3.7
* Working internet connection
* Not having throttled by DataSF already :)

## Installation

* Clone or download this repo from github
```bash 
$ git clone https://github.com/mehmetg/datasf.git
```
* Change into the source folder
```bash
$ cd datasf
```
* If virtualenv is not installed install
```bash
$ pip install virtualenv
```
You may need to be root to execute this command
* Create a python virtualenv
 ```bash
$ virtualenv --python=python3.8 venv && ./venv/bin/activate
```

* Install the module
```
pip install .
```

## Operation

* Basic usage
```bash
$ datasf-cli -h   
usage: datasf-cli [-h] {mobile_food_schedule,mfs} ...

Tool to interact with Data SF data sets

positional arguments:
  {mobile_food_schedule,mfs}
    mobile_food_schedule (mfs)
                        Interacts with mobile food schedule dataset

optional arguments:
  -h, --help            show this help message and exit

```
* Mobile Food Schedule Usage
```bash
datasf-cli mfs -h
usage: datasf-cli mobile_food_schedule [-h] [--query QUERY] [--page-size PAGE_SIZE] [--page-offset PAGE_OFFSET] [--day DAY] [--time TIME]

optional arguments:
  -h, --help            show this help message and exit
  --page-size PAGE_SIZE
                        Number of results to show per page, default: 0
  --page-offset PAGE_OFFSET
                        Results to skip, default: 0
  --day DAY             Day of the week 0: Sunday, ..., 7: Monday, default: today
  --time TIME           Time of the day in 24hr format: HH:MM, default: current time

```

* Auth Settings:

This tool allows setting of the following environment variables to authenticate to the Socrata API.
```
API_KEY: User token (superseeds username/password when set) 
USERNAME: username for the api
PASSWORD: password for the api
``` 
e.g. `$ API_KEY="my-api-key-122" datasf-cli mfs`

The use of environment variables are intentional to avoid plain text input of secrets using stdin and possibly getting
stored.  

## Design Considerations

### Api Usage: 
This tool does minimal data manipulation and limits the size of the data retrieved from the API and the offline 
transformation work to a minimum. 
The data is filtered using the parameters supplied server side and the tool merely formats and paginates as required by 
specifications.  

### Components:

## Socrata Client
It is a very simple implementation that supports the execution of a provided query on a specified back end.
The client support basic user authentication with an api key or username password pair which can be set using environment
variables.
This client is easily extensible with more function and will be a rather thin layer on top of the requests library.

## Mobile Food Schedule Object
This object houses all relevant logic and functionality for the tool. It handles data pagination from the api and user 
interaction (commandline arguments, data output and user input)
The next step for this module would be defining an interface from it and making sure additional modules can 
implement it as well. 
This code could have been very generic using kwargs as params and could be extended without need for a proper interface
or refactor, but use of kwargs generally make code hard to follow and maintain in the long term and cause a lot of runtime 
issues. Therefore the choice was to stick with named parameters with strict typing.

## Command Line Driver

The command line driver handles basic initialization and parsing of command command line arguments.
The parser is set up in a way that more subparsers can be added to the program to extend functionality.

## Notes and Known Issues:

* Log level for the tool can be set using the `LOG_LEVEL` environment variable options are:
```CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG```

* If the user is throttled due to a lack of proper authentication the tool will display an error and quit. User
must wait until the back off period expires or use authentication.

* If the user gets throttled by the API there's no automatic back off just an informative error message. This certainly 
can be improved upon. 
