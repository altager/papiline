import http

from papiline import Chain, HttpHeaderName, ContentType
from py_fake_server import FakeServer


def test_validate_response_code(chain: Chain, server: FakeServer):
    server.on_("get", "/test"). \
        response(status=http.HTTPStatus.OK, body='{"test": "valid_response_code"}',
                 content_type=ContentType.APPLICATION_VND_API_JSON)

    chain \
        .do_request_get("/test") \
        .do_validate_response_code(http.HTTPStatus.OK)


def test_validate_schema(chain: Chain, server: FakeServer):
    schema = {
            "type": "object",
            "properties": {
                "test": {
                    "type": "string"
                }
            }
        }
    server.on_("get", "/test"). \
        response(status=http.HTTPStatus.OK, body='{"test": "validate_schema"}',
                 content_type=ContentType.APPLICATION_VND_API_JSON)
    chain \
        .do_prepare_request(headers={HttpHeaderName.CONTENT_TYPE: ContentType.APPLICATION_VND_API_JSON}) \
        .do_request_get("/test") \
        .do_validate_response_code(http.HTTPStatus.OK) \
        .do_validate_schema(schema)


def test_lazy_execution(chain: Chain, server: FakeServer):
    server.on_("get", "/test"). \
        response(status=http.HTTPStatus.OK, body='{"test": "lazy_exec"}',
                 content_type=ContentType.APPLICATION_VND_API_JSON)

    server.on_("get", "/test/404"). \
        response(status=http.HTTPStatus.NOT_FOUND, content_type=ContentType.APPLICATION_VND_API_JSON)

    # Enable lazy execution and switch back to normal after execute()
    chain \
        .lazy() \
        .do_request_get("/test") \
        .do_validate_response_code(http.HTTPStatus.OK) \
        .do_request_get("/test/404") \
        .do_validate_response_code(http.HTTPStatus.NOT_FOUND) \
        .execute()

    chain.do_request_get("/test") \
        .do_validate_response_code(http.HTTPStatus.OK)
