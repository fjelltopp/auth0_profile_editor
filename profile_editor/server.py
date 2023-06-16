
import json
import os
from urllib.parse import quote_plus, urlencode

import requests
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, flash
import http.client
import logging

from forms import UserDataForm

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

env = os.environ

app = Flask(__name__, template_folder="../templates")
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)
log = logging.getLogger("profile_editor")

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


# Controllers API
def get_user_metadata(mgmt_token, user_id):
    log.debug(f"looking for user: {user_id}")
    headers = {
        'Authorization': f'Bearer {mgmt_token}',
        'Content-Type': 'application/json'
    }
    auth0_domain = env.get("AUTH0_DOMAIN")
    res = requests.get(f'https://{auth0_domain}/api/v2/users/{user_id}', headers=headers)
    res_json = res.json()
    log.debug(f"user: {res_json}")

    return res_json


@app.route("/")
def home():
    user_metadata = {"orgname": "None", "jobtitle": "None"}

    if session and session.get("user"):
        mgmt_token = get_mgmt_token()
        user_metadata = get_user_metadata(mgmt_token, session.get("user").get("userinfo").get("sub"))['user_metadata']

    return render_template(
        "home.html",
        session=session.get("user"),
        user_metadata=user_metadata,
        pretty=json.dumps(session.get("user"), indent=4),
        domain=env.get("AUTH0_DOMAIN"),
        env_file=ENV_FILE
    )


def get_mgmt_token():
    mgmt_client_id = env.get('AUTH0_MGMT_CLIENT_ID')
    mgmt_client_secret = env.get('AUTH0_MGMT_CLIENT_SECRET')
    auth0_domain = env.get("AUTH0_DOMAIN")
    conn = http.client.HTTPSConnection(host=f"{auth0_domain}")
    payload = f"grant_type=client_credentials&client_id={mgmt_client_id}&client_secret={mgmt_client_secret}" \
              f"&audience=https://{auth0_domain}/api/v2/"
    headers = {'content-type': "application/x-www-form-urlencoded"}
    conn.request("POST", f"/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    log.debug(f"payload: {payload}")
    mgmt_token = json.loads(data.decode("utf-8")).get("access_token")
    return mgmt_token


def load_data_from_server(form):
    if session and session.get("user"):
        mgmt_token = get_mgmt_token()
        user_metadata = get_user_metadata(mgmt_token, session.get("user").get("userinfo").get("sub"))['user_metadata']
        form.name.data = session.get("user").get("userinfo").get("name")
        form.email.data = session.get("user").get("userinfo").get("email")
        form.orgname.data = user_metadata.get("orgname", "")
        form.jobtitle.data = user_metadata.get("jobtitle", "")

    return form


@app.route("/profile", methods=['GET', 'POST'])
def profile_read():
    form = UserDataForm()

    flash("Hello!")

    if form.validate_on_submit():
        flash(f'User {form.name.data}, Org={form.orgname.data}')
    elif not form.is_submitted():
        form = load_data_from_server(form)

    return render_template(
        "profile.html",
        form=form
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
