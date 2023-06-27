import os

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask_wtf import CSRFProtect

from ape.healthz import healthz_blueprint
from ape.routes import oauth, app_blueprint

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

env = os.environ


def create_app():
    flask_app = Flask(__name__, template_folder="./templates")
    flask_app.secret_key = env.get("APP_SECRET_KEY")

    oauth.init_app(flask_app)
    csrf = CSRFProtect()
    csrf.init_app(flask_app)

    oauth.register(
        "auth0",
        client_id=env.get("AUTH0_CLIENT_ID"),
        client_secret=env.get("AUTH0_CLIENT_SECRET"),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
    )

    flask_app.register_blueprint(app_blueprint)
    flask_app.register_blueprint(healthz_blueprint)

    return flask_app


app = create_app()
