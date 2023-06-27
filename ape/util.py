import logging
import os

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_wtf import CSRFProtect


log = logging.getLogger("auth0_profile_editor")



