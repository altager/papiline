from papiline import Pipeline, ContentTypes
from py_fake_server import FakeServer


def test_validate_response_code(pipeline: Pipeline, server: FakeServer):
    server.on_("get", "/users"). \
        response(status=200, body='[{"userId": "1"}, {"userId": "2"}]',
                 content_type=ContentTypes.APPLICATION_VND_API_JSON)
    pipeline\
        .do_request_get("/users")\
        .do_validate_response_code(200)


def test_validate_schema(pipeline: Pipeline, server: FakeServer):
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "userId": {
                    "type": "string"
                }
            }
        }
    }
    server.on_("get", "/users"). \
        response(status=200, body='[{"userId": "1"}, {"userId": "2"}]',
                 content_type=ContentTypes.APPLICATION_VND_API_JSON)
    pipeline\
        .do_prepare_request(headers={"Content-Type": ContentTypes.APPLICATION_VND_API_JSON})\
        .do_request_get("/users")\
        .do_validate_response_code(200)\
        .do_validate_schema(schema)
