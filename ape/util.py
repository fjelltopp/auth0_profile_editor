import logging
import os

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_wtf import CSRFProtect


log = logging.getLogger("auth0_profile_editor")


def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.secret_key = env.get("APP_SECRET_KEY")

    oauth = OAuth(app)
    csrf = CSRFProtect()
    csrf.init_app(app)
    domain = env.get("AUTH0_DOMAIN")
    url = f'https://{domain}/.well-known/openid-configuration'

    oauth.register(
        "auth0",
        client_id=env.get("AUTH0_CLIENT_ID"),
        client_secret=env.get("AUTH0_CLIENT_SECRET"),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=url,
    )

    return app, oauth
