"""This package holds the api of the web application
"""

from pblog import factory
from pblog.core import api
from pblog.core import marshmallow
from pblog.blog.api.resources import *  # NOQA


def create_app():
    """creates a new api flask application
    """
    app = factory.create_app(__name__, __path__)
    api.init_app(app)
    marshmallow.init_app(app)

    return app
