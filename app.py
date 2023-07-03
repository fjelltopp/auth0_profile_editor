import os

from dotenv import load_dotenv, find_dotenv
from flask import Flask, request
from flask_babel import Babel
from flask_wtf import CSRFProtect

from ape.healthz import healthz_blueprint
from ape.routes import oauth, app_blueprint

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

env = os.environ


def create_app(config_object=None):
    flask_app = Flask(__name__, template_folder="./templates")

    if not config_object:
        config_object = os.getenv('CONFIG_OBJECT', 'config.Config')
    flask_app.config.from_object(config_object)

    flask_app.secret_key = flask_app.config.get("APP_SECRET_KEY")

    def get_locale():
        if request:
            return request.accept_languages.best_match(app.config['LANGUAGES'])
        else:
            return flask_app.config['DEFAULT_LANGUAGE']

    oauth.init_app(flask_app)
    csrf = CSRFProtect()
    csrf.init_app(flask_app)
    babel = Babel()
    babel.init_app(flask_app, locale_selector=get_locale,
                   default_translation_directories='i18n')
    domain = env.get("AUTH0_DOMAIN")

    url = f'https://{domain}/.well-known/openid-configuration'

    oauth.register(
        "auth0",
        client_id=flask_app.config.get("AUTH0_CLIENT_ID"),
        client_secret=flask_app.config.get("AUTH0_CLIENT_SECRET"),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=url,
    )

    flask_app.register_blueprint(app_blueprint)
    flask_app.register_blueprint(healthz_blueprint)

    return flask_app


app = create_app()
