#Papiline: Build your own requests pipeline 
[![Build Status](https://travis-ci.org/altager/papiline.svg?branch=master)](https://travis-ci.org/altager/papiline)
[![codecov](https://codecov.io/gh/altager/papiline/branch/master/graph/badge.svg)](https://codecov.io/gh/altager/papiline)

**Papiline** is a Python library for constructing request pipelines.
 
## Table of contents
* [Install](#install)
* [Overview](#overview)
* [Getting Started](#getting-started)
* [Documentation by example](#documentation-by-example)

## Install 
`python3 setup.py install`

##Overview

Usually, when we want to create HTTP request we can simply divide it in several stages such as: 
PrepareData -> PrepareRequest -> ExecuteRequest -> ValidateResponse. 
What if we can create representation of such pipeline in our code? That's all this library is about.

As an example - it's very useful for API-test creation.

##Getting Started

Let's start from simple example:

Imagine you have an API endpoint which you want to test (i will use [py_fake_server](https://github.com/Telichkin/py_fake_server)):
```python
from py_fake_server import FakeServer
from http import HTTPStatus

server = FakeServer(host="localhost", port=8081)
server.start()

server.on_("get", "/test"). \
        response(status=HTTPStatus.OK, body='{"test": "valid_response_code"}',
                 content_type="application/json")
```

So, if we will make a GET request to `http://localhost:8081/test?id=1` (let's also add some url params) we will get response: `{"test": "valid_response_code"}` with code `200`

Let's now try to use **papiline** to make a call chain.

First of all we have to create `Chain` instance with necessary params:
```python
from papiline import Chain

chain = Chain("localhost", port="8081")
```

Now let's build our execution pipeline:

```python
chain \
    .do_prepare_data_url_params({"id": "1"})\
    .do_prepare_request(headers={"Content-Type": "application/json"}, cookies={"token": "value"})\
    .do_request_get("/test") \
    .do_validate_response_code(200)
```

If we will execute it we will get such response. There are two entries in console log. Same as the number of stages. 
It tells us what was the pipeline `Context` condition at each stage:
```commandline
.2018-04-04 01:59:23,750 - root - DEBUG - [
	Request data raw: None
	Url params: {'id': '1'}
	Headers: {'Content-Type': 'application/json'}
	Cookies: {'token': 'value'}
	Response data: None
	Response data raw: None
	Status code: None
]
2018-04-04 01:59:23,761 - urllib3.connectionpool - DEBUG - Starting new HTTP connection (1): localhost
2018-04-04 01:59:23,763 - urllib3.connectionpool - DEBUG - http://localhost:8081 "GET /test?id=1 HTTP/1.1" 200 15
2018-04-04 01:59:23,764 - root - DEBUG - [
	Request data raw: None
	Url params: {'id': '1'}
	Headers: {'Content-Type': 'application/json'}
	Cookies: {'token': 'value'}
	Response data: {'test': 'get'}
	Response data raw: {"test": "get"}
	Status code: 200
]
```

That's simple, isn't it?

##Documentation by example

`NOTE: On each stage of pipeline you can get Context variables(response_data, status_code etc) simply 
by using dot expression. Example: chain.context.response_data. 
`

Create pipeline:
```python
chain = Chain("localhost")
```

Create GET request for `http://localhost/test?id=1`, validate response code and validate json-schema:
```python

schema = {
            "type": "object",
            "properties": {
                "test": {
                    "type": "string"
                }
            }
        }

chain \
    .do_prepare_data_url_params({"id": "1"})\
    .do_prepare_request(headers={"Content-Type": "application/json"}, cookies={"token": "value"})\
    .do_request_get("/test")\
    .do_validate_response(200)\
    .do_validate_schema(schema)
```

GET with 404 -> POST with 201 -> GET with 200 -> PATCH with 200 -> GET with 200 (same headers and cookies but different data for POST and PATCH):
```python
chain \
    .do_prepare_request(headers={"Content-Type": "application/json"}, cookies={"token": "value"})\
    .do_request_get("/test")\
    .do_validate_response(404)\
        .do_prepare_data_json({"data": "value"})\
        .do_request_post("/test")\
        .do_validate_response(201)\
            .do_request_get("/test")\
            .do_validate_response(200)\
                .do_prepare_data_json_update({"data": "new_value"})\
                .do_request_patch(200)\
                    .do_request_get("/test")\
                    .do_validate_response(200)
```
Accessing to context variables:

```python
req = chain \
        .do_prepare_data_url_params({"id": "1"}) \
        .do_prepare_request(headers={"Content-Type": "application/json"}, cookies={"token": "value"}) \
        .do_request_get("/test")

get_response_data_dict = req.context.response_data
chain \
    .do_validate_response_code(200)

# Clear prev url-params and make next request
chain \
    .do_prepare_data_url_params(None)\
    .do_request_get("/test2")
```

Lazy evaluation. Full pipeline will execute only when `.execute()` function will be called:
```python
# Enable lazy execution and switch back to normal after execute()
chain \
    .lazy() \
    .do_request_get("/test") \
    .do_validate_response_code(200) \
        .do_request_get("/test/404") \
        .do_validate_response_code(404) \
            .execute()
```





