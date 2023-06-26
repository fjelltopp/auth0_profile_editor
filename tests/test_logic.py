from unittest.mock import patch

import pytest

import ape.logic as logic

FT_MEMBER = "ft_member_id"
COTE_EDITOR = 'cote_editor_id'
FT_ADMIN = 'ft_admin_id'

ENV_DATA = {
    "AUTH0_MGMT_CLIENT_ID": "AUTH0_MGMT_CLIENT_ID_value",
    "AUTH0_MGMT_CLIENT_SECRET": "AUTH0_MGMT_CLIENT_SECRET_value"
}


# @pytest.fixture(scope='module')
# def vcr_config():
#     return {
#         # Replace the Authorization request header with "DUMMY" in cassettes
#         # "filter_headers": [('authorization', 'Bearer: fake-bearer-token')],
#     }


@pytest.mark.vcr
def test_get_mgmt_token():
    token = logic.get_mgmt_token()

    assert token == "mgmt_token_value"


@pytest.mark.vcr
def test_load_user_data():
    form = DummyUserDataForm()

    form = logic.load_data_from_server_to_form(form, FT_MEMBER)

    assert_correct_user_data(form, "Fjelltopp Member", "ft_member@fjelltopp.org", "FT Ltd", "Member")


@pytest.mark.vcr
def test_load_data_from_server_when_userdata_empty():
    form = DummyUserDataForm()

    form = logic.load_data_from_server_to_form(form, COTE_EDITOR)

    assert_correct_user_data(form, "", "ct_editor@cote.org", "", "")


@pytest.mark.vcr()
def test_load_data_from_server_when_only_fullname_in_user_metadata():
    form = DummyUserDataForm()

    form = logic.load_data_from_server_to_form(form, FT_ADMIN)

    assert_correct_user_data(form, "Fjelltopp Admin", "ft_admin@fjelltopp.org", "", "")


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


