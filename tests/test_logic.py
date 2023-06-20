from unittest.mock import patch

import pytest

import ape.logic as logic

ENV_DATA = {
    "AUTH0_MGMT_CLIENT_ID": "AUTH0_MGMT_CLIENT_ID_value",
    "AUTH0_MGMT_CLIENT_SECRET": "AUTH0_MGMT_CLIENT_SECRET_value"
}


def get_env_value(key):
    return ENV_DATA.get(key)


def session_get_value(key):
    if key == "user":
        return {
            "sub": "auth0|user_id",
            "name": "Some User Name",
            "email": "user@domain.com"
        }


@pytest.fixture
def http_server(httpserver):
    ENV_DATA['AUTH0_DOMAIN'] = f"{httpserver.host}:{httpserver.port}"
    return httpserver


@patch("ape.logic.get_protocol")
@patch("ape.logic.util.env.get")
def test_get_mgmt_token(env_get, get_protocol, http_server):
    env_get.side_effect = get_env_value
    get_protocol.return_value = "http"
    auth0_domain = f"{http_server.host}:{http_server.port}"
    expected_payload = f"grant_type=client_credentials&client_id=AUTH0_MGMT_CLIENT_ID_value" \
                       "&client_secret=AUTH0_MGMT_CLIENT_SECRET_value" \
                       f"&audience=https://{auth0_domain}/api/v2/"
    http_server.expect_request("/oauth/token", data=expected_payload) \
        .respond_with_data(response_data='{"access_token": "mgmt_token_value"}')

    token = logic.get_mgmt_token()

    assert token == "mgmt_token_value"


@patch("ape.logic.get_protocol")
@patch("ape.logic.util.env.get")
@patch("ape.logic.get_mgmt_token")
@patch("ape.logic.get_session")
def test_get_user_metadata(session, get_mgmt_token, env_get, get_protocol, http_server):
    env_get.side_effect = get_env_value
    session.return_value.get.side_effect = session_get_value
    get_mgmt_token.return_value = "mgmt_token_value"
    get_protocol.return_value = "http"
    user_metadata = '{"user_metadata": {"orgname": "", "jobtitle": ""}}'
    http_server.expect_request("/api/v2/users/auth0|user_id").respond_with_data(user_metadata)

    user_metadata = logic.get_user_metadata()

    assert user_metadata == {"orgname": "", "jobtitle": ""}
