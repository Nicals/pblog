"""Web part of PBlog.

This module holds a pblog flask extension.
Additionally, a factory is provided to be able to quickly have a running
blog.
"""


class PBlog:
    """Entry point for the Flask PBlog extension.

        >>> from flask import Flask
        >>> from flask_pblog import PBlog
        >>> app = Flask()
        >>> PBlog(app)

    Or using the factory pattern:

        >>> from flask import Flask
        >>> from flask_pblog import PBlog
        >>> app = Flask()
        >>> pblog = PBlog()
        >>> pblog.init_app(app)
    """
    def __init__(self, app=None, storage=None):
        self.app = app
        self.storage = storage

        if app is not None and self.storage is not None:
            self.init_app(app)

    def init_app(self, app, storage=None):
        self.app = app
        self.storage = storage or self.storage
        from flask_pblog.views import blueprint
        blueprint.template_folder = app.config.get('PBLOG_TEMPLATE_FOLDER', 'templates')
        app.register_blueprint(blueprint)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['pblog'] = self
