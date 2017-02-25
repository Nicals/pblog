"""This module contains the Flask app factory.
"""

import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from pblog.core import db

ENV_SETTINGS = 'PBLOG_SETTINGS'


def create_app(package_name, package_path):
    """Creates a new application

    """
    app = Flask(package_name)

    app.config.from_object('pblog.settings')

    if ENV_SETTINGS in os.environ:
        app.config.from_envvar(ENV_SETTINGS)

    db.init_app(app)
    DebugToolbarExtension(app)

    return app
