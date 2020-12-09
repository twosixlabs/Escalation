"""
Copyright [2020] [Two Six Labs, LLC]
Licensed under the Apache License, Version 2.0
"""

from flask import current_app
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from utility.constants import DEVELOPMENT
from app_deploy_data.app_settings import USERS


users = {u: generate_password_hash(p) for u, p in USERS.items()}
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    # don't require authentication when running in development mode in wizard
    if current_app.config.get("ENV") == DEVELOPMENT:
        return username
    if username in users and check_password_hash(users.get(username), password):
        return username
    return False


@auth.error_handler
def basic_auth_error(status):
    return "User not authenticated for admin actions", 401
