Quickstart
==========

``PBlog`` is constructed on two main parts.
The first one is a flask extension in the `flask_pblog` module.
The second one contains the command line interface and core functionalities
in the `pblog` module.

Install PBlog
-------------

For now, PBlog is not published on PyPI, so it must be installed from source.

.. code:: console

   $ python setup.py install


Building the web server
-----------------------

The next step is to build a Flask application that will use the ``flask_blog`` extension.

.. code:: python
   
   # file app.py
   from os import path

   from flask import Flask, send_from_directory
   from flask_sqlalchemy import SQLAlchemy
   import flask_pblog
   from flask_pblog.storage import Storage
   from markdown import Markdown

   # the directory of the current file
   BASE_PATH = path.dirname(path.abspath(__file__)à)

   # default PBlog css is stored there.
   static_folder = path.join(path.dirname(flask_pblog.__file__), 'static')
   # resource_path is the directory where we will store posts related files
   # (images, source code, ...)
   # see the *Markdown Posts / Local resources* for more information on this
   resource_path = path.join(BASE_PATH, 'resources')

   app = Flask(__name__, static_folder=static_folder)

   app.config['SECRET_KEY'] = 'not-so-secret'
   # database configuration
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path.join(BASE_PATH, 'db.sqlite')
   # PBlog configuration
   app.config['PBLOG_CONTRIBUTORS'] = {
       'admin': 'pbkdf2:sha256:.....',
   }
   # where are stored posts related resources
   app.config['PBLOG_RESOURCES_PATH'] = resource_path
   # how are they accessed
   app.config['PBLOG_RESOURCES_URL'] = '/resources/'

   # we need a markdown instance to create or update posts
   md = Markdown(
       extensions={
           'markdown_extra.meta',
           'markdown_extra.summary',
           'markdown_extra.resource_path',
       },
       extensions_config={
           'markdown_extra': {
               'root_path': '/resources/',
           },
       },
   )

   # create the SQLAlchemy extesions
   db = SQLAlchemy(app)
   flask_pblog.PBlog(app, storage=Storage(session=db.session), markdown=md)


   @app.route('/resources/<path:path>')
   def serve_post_resource(path):
       return send_from_directory(resource_path, path)


   if __name__ == '__main__':
       app.run()


Before you can run the the web server, the database must be created.
From a python terminal:

.. code:: python

   from app import db
   from flask_pblog.models import Base

   Base.metadata.create_all(bind=db.engine)

The resource directory (defined in *PGLOG_RESOURCES_PATH*) must also be created.
The server can now be started with

.. code:: console

   $ mkdir resources
   $ python app.py

User are stored in memory. There aren't any session management on the server.
Users are only here to allow to upload some new posts from the client application.

PBlog is shipped with some default static files (only CSS).
You can use your own static files or use the provided ones as shown in
the example.


Using the command line client
-----------------------------

Once the web server is up and running, the command line part of the application
can be setup.

A ``pblog.ini`` file must be created.
This file is used to tell pblog where we will want to upload new posts.

When using ``P-Blog`` command line interface, a ``pblog.ini`` file must be
present in the current directory.

The url to the blog and the username to authenticate with will be stored in it.
Several environment (PBlog instances) can be configured independently.

.. code-block:: ini

   [pblog]
   ; using [pblog:default] section as default environment
   env = default

   [pblog:default]
   username = admin
   url = http://blog.example.org/

   [pblog:testing]
   username = admin
   url = http://127.0.0.1:8000/blog/
   wsgi = blog.app

You can then start writing some blog posts.
Lets setup every posts in their own directory, so we will have the following structure:

.. code-block:: text

   app.py
   /resources/
   pblog.ini
   /blog/
      first-post/
         first-post.md
         imgs/
            fancy-image.png

The blog post will have the following content:

.. code-block:: text

   ---
   title: This is the first blog post
   topic: Testing
   ---

   [summary]
   This is my first blog post.

   ![A great picture](imgs/fancy-image.png)

   We can link some images to the post.

Any resources that need to be shipped with the post must be defined by a path relative to the markdown file.
Those path will be resolved when publishing the post.

When we are ready, we can publish the post.

.. code-block:: console

   $ python -mpblog publish blog/first-post/first-post.md

See :doc:`writing-posts` to see how to write posts.


.. command-output:: python -mpblog --help
   :cwd: ..

The ``env`` option can be used to select the environment to load.
The ``ini`` option sets the ``pblog.ini`` file to load.
The ``wsgi`` option sets a local wsgi application that can be started in
background by using the ``-a`` flag of the command line interface.
