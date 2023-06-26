import json

import requests
from flask import session
import ape.util as util

log = util.log


def get_user_data(user_id):
    mgmt_token = get_mgmt_token()

    log.debug(f"looking for user: {user_id}")
    headers = {
        'Authorization': f'Bearer {mgmt_token}',
        'Content-Type': 'application/json'
    }
    auth0_domain = util.env.get("AUTH0_DOMAIN")
    url = f'{get_protocol()}://{auth0_domain}/api/v2/users/{user_id}'
    res_json = requests.get(url, headers=headers).json()

    return res_json


def get_protocol():
    return "https"


def get_session():
    return session


def get_mgmt_token():
    client_id = util.env.get('AUTH0_CLIENT_ID')
    client_secret = util.env.get('AUTH0_CLIENT_SECRET')
    auth0_domain = util.env.get("AUTH0_DOMAIN")
    payload = f"grant_type=client_credentials&client_id={client_id}" \
              f"&client_secret={client_secret}" \
              f"&audience=https://{auth0_domain}/api/v2/"
    url = f'{get_protocol()}://{auth0_domain}/oauth/token'
    headers = {'content-type': "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    mgmt_token = response.json().get("access_token")

    return mgmt_token


def load_data_from_server_to_form(form, user_id):
    user_data = get_user_data(user_id)
    user_metadata = user_data.get("user_metadata", {})

    form.name.data = user_metadata.get("full_name", "")
    form.email.data = user_data.get("email", "")
    form.orgname.data = user_metadata.get("orgname", "")
    form.jobtitle.data = user_metadata.get("jobtitle", "")

    return form


def convert_to_data_object(form):
    return {
        "email": form.email.data,
        "user_metadata": {
            "full_name": form.name.data,
            "orgname": form.orgname.data,
            "jobtitle": form.jobtitle.data
        }
    }


def update_user_data(form, user_id):
    data = convert_to_data_object(form)
    mgmt_token = get_mgmt_token()
    headers = {
        'Authorization': f'Bearer {mgmt_token}',
        'Content-Type': 'application/json'
    }
    auth0_domain = util.env.get("AUTH0_DOMAIN")
    url = f'https://{auth0_domain}/api/v2/users/{user_id}'
    result = requests.patch(url, headers=headers, data=json.dumps(data))
    if result.status_code != 200:
        log.error(f"Couldn't save user data: {result.content}")
        raise ProfileEditingError()


class ProfileEditingError(Exception):
    pass
