"""This package holds the frontend blog web application.

"""

from pblog import factory
from pblog.blog.frontend.blueprint import blueprint


def create_app():
    """Creates a new frontend flask application.
    """
    app = factory.create_app(__name__, __path__)
    app.register_blueprint(blueprint)

    return app
