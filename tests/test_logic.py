from unittest.mock import patch

import pytest

import ape.logic as logic

USER_ID = "auth0|837f0cc8ee2d"

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
def test_load_user_data(session, get_mgmt_token, env_get, get_protocol, http_server):
    env_get.side_effect = get_env_value
    session.return_value.get.side_effect = session_get_value
    get_mgmt_token.return_value = "mgmt_token_value"
    get_protocol.return_value = "http"
    form = DummyUserDataForm()
    response = '{"email": "first_user@fjelltopp.org", ' \
               '"user_metadata": {"orgname": "Fjelltopp", "jobtitle": "Epidemiologist", "full_name": "First User"}}'
    http_server.expect_request(f"/api/v2/users/{USER_ID}").respond_with_data(response)

    form = logic.load_data_from_server_to_form(form, USER_ID)

    assert_correct_user_data(form, "First User", "first_user@fjelltopp.org", "Fjelltopp", "Epidemiologist")


@patch("ape.logic.get_protocol")
@patch("ape.logic.util.env.get")
@patch("ape.logic.get_mgmt_token")
@patch("ape.logic.get_session")
def test_load_data_from_server_when_userdata_empty(session, get_mgmt_token, env_get, get_protocol, http_server):
    env_get.side_effect = get_env_value
    session.return_value.get.side_effect = session_get_value
    get_mgmt_token.return_value = "mgmt_token_value"
    get_protocol.return_value = "http"
    form = DummyUserDataForm()
    response = '{"email": "first_user@fjelltopp.org", "user_metadata": {}}'
    http_server.expect_request(f"/api/v2/users/{USER_ID}").respond_with_data(response)

    form = logic.load_data_from_server_to_form(form, USER_ID)

    assert_correct_user_data(form, "", "first_user@fjelltopp.org", "", "")


@patch("ape.logic.get_protocol")
@patch("ape.logic.util.env.get")
@patch("ape.logic.get_mgmt_token")
@patch("ape.logic.get_session")
def test_load_data_from_server_when_only_orgname_in_user_metadata(session, get_mgmt_token, env_get, get_protocol,
                                                                  http_server):
    env_get.side_effect = get_env_value
    session.return_value.get.side_effect = session_get_value
    get_mgmt_token.return_value = "mgmt_token_value"
    get_protocol.return_value = "http"
    form = DummyUserDataForm()
    user_metadata = '{"email": "first_user@fjelltopp.org", "user_metadata": {"orgname": "Fjelltopp"}}'
    http_server.expect_request(f"/api/v2/users/{USER_ID}").respond_with_data(user_metadata)

    form = logic.load_data_from_server_to_form(form, USER_ID)

    assert_correct_user_data(form, "", "first_user@fjelltopp.org", "Fjelltopp", "")


def assert_correct_user_data(form, full_name, email, orgname, jobtitle):
    assert form.name.data == full_name
    assert form.email.data == email
    assert form.orgname.data == orgname
    assert form.jobtitle.data == jobtitle


class Holder:
    data = ""


class DummyUserDataForm:
    name = Holder()
    email = Holder()
    orgname = Holder()
    jobtitle = Holder()


