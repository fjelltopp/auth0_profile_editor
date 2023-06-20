import http.client
from unittest.mock import patch

import pytest

from ape import logic

ENV_DATA = {
    "AUTH0_DOMAIN": "AUTH0_DOMAIN_value",
    "AUTH0_MGMT_CLIENT_ID": "AUTH0_MGMT_CLIENT_ID_value",
    "AUTH0_MGMT_CLIENT_SECRET": "AUTH0_MGMT_CLIENT_SECRET_value"
}


@pytest.fixture
def http_connection(httpserver):
    return httpserver, http.client.HTTPConnection(host=httpserver.host, port=httpserver.port)


class TestUpdatingUser:
    @patch("ape.logic.get_protocol")
    @patch("ape.logic.env.get")
    @patch("ape.logic.get_connection")
    def test_get_mgmt_token(self, get_connection, env_get, get_protocol, http_connection):
        server, conn = http_connection
        get_connection.return_value = conn

        def get_env_value(key):
            return ENV_DATA.get(key)

        env_get.side_effect = get_env_value
        get_protocol.return_value = "http"
        expected_payload = f"grant_type=client_credentials&client_id=AUTH0_MGMT_CLIENT_ID_value" \
                           "&client_secret=AUTH0_MGMT_CLIENT_SECRET_value" \
                           "&audience=https://AUTH0_DOMAIN_value/api/v2/"

        server.expect_request("/oauth/token", data=expected_payload) \
            .respond_with_data(response_data='{"access_token": "mgmt_token_value"}'.encode("utf-8"))

        token = logic.get_mgmt_token()

        assert token == "mgmt_token_value"

