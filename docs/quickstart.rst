Quickstart
==========

Starting the web server
-----------------------

Settings are set in a python settings file.
The path of this file is provided to P-Blog by setting it in an ``PBLOG_SETTINGS``
environment variable.

=========================== ========== ================================================================
``DEBUG``                   **bool**   enable/disable debug mode
``SECRET_KEY``              **string** the secret key
``SQLALCHEMY_DATABASE_URI`` **string** the database URI to use. Example:
                                          + sqlite:////tmp/db.sqlite3
``PBLOG_CONTRIBUTORS``      **dict**   a dictionary mapping username to hashed passwords. For example:
                                          + 'admin': 'pbkdf2:...'
``PBLOG_TEMPLATE_FOLDER``   **string** path to override default Pblog templates. Not required.
                                       See :doc:`customize`.
=========================== ========== ================================================================

Create the database

.. code-block:: console

  $ python manage.py upgrade

The web server is started by the ``wsgi.py`` script.

.. code-block:: console

   $ PBLOG_SETTINGS=~/blog.settings.py python wsgi.py


Using the command line
----------------------

A ``pblog.ini`` file must be created.
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
