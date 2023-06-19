import http.client
import json

import requests
from flask import session

from app import log, env


def get_user_metadata():
    mgmt_token = get_mgmt_token()
    user_metadata = {"orgname": "", "jobtitle": ""}

    if session:
        user_id = session.get("user").get("userinfo").get("sub")

        log.debug(f"looking for user: {user_id}")
        headers = {
            'Authorization': f'Bearer {mgmt_token}',
            'Content-Type': 'application/json'
        }
        auth0_domain = env.get("AUTH0_DOMAIN")
        res_json = requests.get(f'https://{auth0_domain}/api/v2/users/{user_id}', headers=headers).json()
        user_metadata = res_json.get("user_metadata", user_metadata)

    return user_metadata


def get_mgmt_token():
    mgmt_client_id = env.get('AUTH0_MGMT_CLIENT_ID')
    mgmt_client_secret = env.get('AUTH0_MGMT_CLIENT_SECRET')
    auth0_domain = env.get("AUTH0_DOMAIN")
    conn = http.client.HTTPSConnection(host=f"{auth0_domain}")
    payload = f"grant_type=client_credentials&client_id={mgmt_client_id}&client_secret={mgmt_client_secret}" \
              f"&audience=https://{auth0_domain}/api/v2/"
    headers = {'content-type': "application/x-www-form-urlencoded"}
    conn.request("POST", f"/oauth/token", payload, headers)
    response = conn.getresponse()
    data = response.read()

    mgmt_token = json.loads(data.decode("utf-8")).get("access_token")

    return mgmt_token


def load_data_from_server(form):
    if session and session.get("user"):
        user_metadata = get_user_metadata()
        form.name.data = session.get("user").get("userinfo").get("name")
        form.email.data = session.get("user").get("userinfo").get("email")
        form.orgname.data = user_metadata.get("orgname", "")
        form.jobtitle.data = user_metadata.get("jobtitle", "")

    return form


def convert_to_data_object(form):
    return {
        "name": form.name.data,
        "email": form.email.data,
        "user_metadata": {
            "orgname": form.orgname.data,
            "jobtitle": form.jobtitle.data
        }
    }


def update_user_data(form, user_id):
    data_object = convert_to_data_object(form)
    mgmt_token = get_mgmt_token()
    headers = {
        'Authorization': f'Bearer {mgmt_token}',
        'Content-Type': 'application/json'
    }
    auth0_domain = env.get("AUTH0_DOMAIN")
    url = f'https://{auth0_domain}/api/v2/users/{user_id}'
    result = requests.patch(url, headers=headers, data=json.dumps(data_object))
    if result.status_code != 200:
        log.error(f"Couldn't save user data: {result.content}")
        raise ProfileEditingError()


class ProfileEditingError(Exception):
    pass

