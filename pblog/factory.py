"""This module contains the Flask app factory.
"""

import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from pblog.core import db, marshmallow
from pblog.api.resources import blueprint as api_blueprint
from pblog.frontend.blueprint import blueprint as blog_blueprint

ENV_SETTINGS = 'PBLOG_SETTINGS'


def create_app():
    """Creates a new application

    """
    app = Flask(__name__)

    # setup settings
    app.config.from_object('pblog.settings')

    if ENV_SETTINGS in os.environ:
        app.config.from_envvar(ENV_SETTINGS)

    if 'PBLOG_TEMPLATE_FOLDER' in app.config:
        app.template_folder = app.config['PBLOG_TEMPLATE_FOLDER']

    # init apps
    db.init_app(app)
    marshmallow.init_app(app)
    DebugToolbarExtension(app)

    # register blueprints
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(blog_blueprint)

    return app
