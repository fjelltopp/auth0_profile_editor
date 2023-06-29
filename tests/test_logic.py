from unittest import mock

import pytest

import ape.logic as logic

FT_MEMBER = "ft_member_id"
COTE_EDITOR = 'cote_editor_id'
FT_ADMIN = 'ft_admin_id'

ENV_DATA = {
    "AUTH0_MGMT_CLIENT_ID": "AUTH0_MGMT_CLIENT_ID_value",
    "AUTH0_MGMT_CLIENT_SECRET": "AUTH0_MGMT_CLIENT_SECRET_value"
}


@pytest.mark.vcr
def test_get_mgmt_token():
    token = logic.get_mgmt_token()

    assert token == "mgmt_token_value"


@pytest.mark.vcr
def test_load_user_data():
    form = DummyUserDataForm()

    form = logic.load_data_from_server_to_form(form, FT_MEMBER)

    assert_correct_user_data(form, "Fjelltopp Member",
                             "ft_member@fjelltopp.org", "FT Ltd", "Member")


@pytest.mark.vcr
def test_load_data_from_server_when_userdata_empty():
    form = DummyUserDataForm()

    form = logic.load_data_from_server_to_form(form, COTE_EDITOR)

    assert_correct_user_data(form, "", "ct_editor@cote.org", "", "")


@pytest.mark.vcr
def test_load_data_from_server_when_only_fullname_in_user_metadata():
    form = DummyUserDataForm()

    form = logic.load_data_from_server_to_form(form, FT_ADMIN)

    assert_correct_user_data(form, "Fjelltopp Admin",
                             "ft_admin@fjelltopp.org", "", "")


@pytest.mark.vcr
def test_update_user_data():
    form = DummyUserDataForm()
    form.email.data = "truly_test@fjelltopp.org"
    form.name.data = "Truly Test User"
    form.orgname.data = "Fjelltopp"
    form.jobtitle.data = "Test user"

    logic.update_user_data(form, "user_id")


@mock.patch('ape.logic.log')
@pytest.mark.vcr
def test_update_user_data_should_throw_upon_error(log):
    form = DummyUserDataForm()
    form.email.data = "some@email.com"
    form.name.data = "Full Name"
    form.orgname.data = "Fjelltopp"
    form.jobtitle.data = "Job Title"

    with pytest.raises(logic.ProfileEditingError):
        logic.update_user_data(form, "user_id")

    error_msg = '{"statusCode":401,"error":"Unauthorized",' \
                '"message":"Invalid token"}'
    log.error.assert_called_once_with(
        f'Couldn\'t save user data: b\'{error_msg}\'')


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
