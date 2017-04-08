"""Web part of PBlog.

This module holds a pblog flask extension.
Additionally, a factory is provided to be able to quickly have a running
blog.
"""

import pathlib


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
    def __init__(self, app=None, storage=None, markdown=None):
        self.app = app
        self.storage = storage
        self.markdown = markdown

        if app is not None and self.storage is not None:
            self.init_app(app)

    def init_app(self, app, storage=None, markdown=None):
        self.app = app
        self.storage = storage or self.storage
        self.markdown = markdown or self.markdown
        self.post_resource_path = pathlib.Path(
            app.config['PBLOG_RESOURCES_PATH'])
        self.post_resource_url = app.config['PBLOG_RESOURCES_URL']
        if not self.post_resource_url.endswith('/'):
            self.post_resource_url = self.post_resource_url + '/'
        from flask_pblog.views import blueprint as blog_bp
        from flask_pblog.resources import blueprint as resource_bp
        blog_bp.template_folder = app.config.get('PBLOG_TEMPLATE_FOLDER', 'templates')
        app.register_blueprint(blog_bp)
        app.register_blueprint(resource_bp, url_prefix='/api')

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['pblog'] = self
