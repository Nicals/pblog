"""This package holds the api of the web application
"""

from pblog import factory
from pblog.core import marshmallow
from pblog.blog.api.resources import blueprint


def create_app():
    """creates a new api flask application
    """
    app = factory.create_app(__name__, __path__)
    marshmallow.init_app(app)
    app.register_blueprint(blueprint, url_prefix='/api')

    return app
