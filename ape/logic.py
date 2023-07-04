import json
import logging
import os

import requests
from flask import session

log = logging.Logger(__name__)
env = os.environ


def get_user_data(user_id):
    mgmt_token = get_mgmt_token()

    log.debug(f"looking for user: {user_id}")
    headers = {
        'Authorization': f'Bearer {mgmt_token}',
        'Content-Type': 'application/json'
    }
    auth0_domain = env.get("AUTH0_DOMAIN")
    url = f'{get_protocol()}://{auth0_domain}/api/v2/users/{user_id}'
    res_json = requests.get(url, headers=headers).json()

    return res_json


def get_protocol():
    return "https"


def get_session():
    return session


def get_mgmt_token():
    client_id = env.get('AUTH0_CLIENT_ID')
    client_secret = env.get('AUTH0_CLIENT_SECRET')
    auth0_domain = env.get("AUTH0_DOMAIN")
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
    data_object = convert_to_data_object(form)
    url = f'/api/v2/users/{user_id}'
    result = execute_mgmt_api_request(method="patch",
                                      url=url, data_object=data_object)
    if result.status_code != 200:
        log.error(f"Couldn't save user data: {result.content}")
        raise ProfileEditingError()


def execute_mgmt_api_request(method, url, data_object=None):
    mgmt_token = get_mgmt_token()
    headers = {
        'Authorization': f'Bearer {mgmt_token}',
        'Content-Type': 'application/json'
    }
    auth0_domain = env.get("AUTH0_DOMAIN")
    data = json.dumps(data_object) if data_object else None
    full_url = f'https://{auth0_domain}{url}'
    result = requests.request(method=method,
                              url=full_url, headers=headers, data=data)
    return result


def get_password_change_url(user_id):
    url = '/api/v2/tickets/password-change'
    data_object = {"user_id": user_id,
                   "client_id": env.get("AUTH0_CLIENT_ID")}
    result = execute_mgmt_api_request(
        method="post", url=url, data_object=data_object)

    if result.status_code != 201:
        log.error(f"Couldn't get password change URL: {result.content}")
        raise ProfileEditingError()

    return result.json().get("ticket")


class ProfileEditingError(Exception):
    pass
