Settings
========


=============================== ========== ================================================================
``DEBUG``                       **bool**   enable/disable debug mode
``SECRET_KEY``                  **string** the secret key
``SQLALCHEMY_DATABASE_URI``     **string** the database URI to use. Example:
                                             + sqlite:////tmp/db.sqlite3
``PBLOG_CONTRIBUTORS``          **dict**   a dictionary mapping username to hashed passwords. For example:
                                             + 'admin': 'pbkdf2:...'
``PBLOG_TEMPLATE_FOLDER``       **string** path to override default Pblog templates. Not required.
                                           See :doc:`customize`.
``PBLOG_MARKDOWN_EXTENSIONS``   **list**   a list of markdown extensions to enable. ``markdown_extra.meta``
                                           and ``markdown_extra.summary`` are required and will be automatically
                                           enabled.
``PBLOG_MARKDOWN_EXT_SETTINGS`` **dict**   a dictionary of markdown extension configuration.
                                           see `python-mardown documentation <http://pythonhosted.org/Markdown/reference.html>`_
                                           for more details.
=============================== ========== ================================================================
