import pytest

from py_fake_server import FakeServer
from papiline import Chain


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
def chain() -> Chain:
    return Chain("localhost", port="8081")
