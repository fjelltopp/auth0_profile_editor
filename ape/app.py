import os
import logging

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_wtf import CSRFProtect
from wtforms.csrf.core import CSRF

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

log = logging.getLogger("profile_editor")


def create_app():
    env = os.environ

    app = Flask(__name__, template_folder="../templates")
    app.secret_key = env.get("APP_SECRET_KEY")

    oauth = OAuth(app)
    csrf = CSRFProtect()
    csrf.init_app(app)

    oauth.register(
        "auth0",
        client_id=env.get("AUTH0_CLIENT_ID"),
        client_secret=env.get("AUTH0_CLIENT_SECRET"),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
    )

    return app, oauth
