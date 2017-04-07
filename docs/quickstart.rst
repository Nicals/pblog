Quickstart
==========

``PBlog`` is constructed on two main parts.
The first one is a flask extension in the `flask_pblog` module.
The second one contains the command line interface and core functionalities
in the `pblog` module.

Building the web server
-----------------------

Build the web part of the blog from a flask application using the ``flask_blog``
extension.

This extensions must be provided with a :class:`~flask_pblog.storage.Storage` instance.
The storage provided with Pblog uses SQLAlchemy, so you should provide it with
a session instance.

It should also be given a `markdown.Markdown` instance that will be
used to convert markdown post into proper HTML.
This instance must have at least the `markdown_extra.meta.MetaExtension`
and `markdown_extra.summary.SummaryExtension` enabled.

.. code:: python

   import os

   from flask import Flask
   from flask_sqlalchemy import SQLAlchemy
   import flask_pblog
   from flask_pblog import PBlog
   from flask_pblog.storage import Storage
   from markdown import Markdown

   static_folder = os.path.join(
       os.path.dirname(flask_pblog.__file__), 'static')

   app = Flask(__name__, static_folder=static_folder)
   # for Flask
   app.config['SECRET_KEY'] = 'not-so-secret'
   # for SQLAlchemy
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
   # list of contributors
   app.config['PBLOG_CONTRIBUTORS'] = {
       'admin': 'pbkdf2:.....',
   }
   db = SQLAlchemy(app)
   md = Markdown(extensions=['markdown_extra.meta', 'markdown_extra.summary'])
   PBlog(app, storage=Storage(markdown=db.session, markdown=md)

   app.run()

Contributors for the blog are stored in a dictionary in the settings.
This dictionary maps a username to a hashed passsword.

PBlog is shipped with some default static files (only CSS).
You can use your own static files or use the provided ones as shown in
the example.


Using the command line
----------------------

Once the web server is up and running, the command line part of the application
can be setup.

A ``pblog.ini`` file must be created.
This file is used to tell pblog where we will want to upload new posts.

When using ``P-Blog`` command line interface, a ``pblog.ini`` file must be
present in the current directory.

The url to the blog and the username to authenticate with will be stored in it.
Several environment can be configured independently.

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


.. code-block:: console

   $ python -mpblog publish ~/blog/my-post.md

See :doc:`writing-posts` to see how to write posts.


The ``env`` option can be used to select the environment to load.
The ``ini`` option sets the ``pblog.ini`` file to load.


.. command-output:: python -mpblog --help
   :cwd: ..
