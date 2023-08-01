import logging
import os


class Config(object):
    ENV_TYPE = os.getenv("ENV_TYPE")
    JSON_LOGGING = (os.getenv("JSON_LOGGING", 'false').lower() == 'true')
    LOGGING_LEVEL = logging.INFO
    LANGUAGES = os.getenv('APE_LANGUAGES', 'en,fr,pt_PT').split(',')
    DEFAULT_LANGUAGE = os.getenv('APE_DEFAULT_LANGUAGE', 'en')
    AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
    AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
    APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')


class Testing(Config):
    TESTING = True
    AUTH0_DOMAIN = 'fake-auth0-domain'
    AUTH0_CLIENT_ID = 'client_id'
    AUTH0_CLIENT_SECRET = 'client_secret'
    APP_SECRET_KEY = '1234567890abcdef'


class Development(Config):
    DEBUG = True


class Production(Config):
    PRODUCTION = True
    LOGGING_LEVEL = logging.ERROR
    JSON_LOGGING = (os.getenv("JSON_LOGGING", 'true').lower() == 'true')
