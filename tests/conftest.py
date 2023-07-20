import pytest

from app import create_app


@pytest.fixture(scope="session")
def test_app():
    return create_app(config_object='config.Testing')


@pytest.fixture
def test_client(test_app):
    with test_app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup(test_app):
    with test_app.app_context():
        yield
