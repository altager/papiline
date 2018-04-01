import pytest

from py_fake_server import FakeServer
from papiline.papiline_core import Pipeline


@pytest.fixture(scope="session")
def server() -> FakeServer:
    server = FakeServer(host="localhost", port=8081)
    server.start()
    yield server
    server.stop()


@pytest.fixture(autouse=True)
def clear_server(server: FakeServer) -> None:
    server.clear()
    yield
    server.clear()


@pytest.fixture(scope='session')
def pipeline() -> Pipeline:
    return Pipeline().do_pipeline_init("localhost", port="8081")
