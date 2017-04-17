API
===

Pblog
-----

Package
~~~~~~~

.. automodule:: pblog.package

   .. autofunction:: read_package

   .. autofunction:: build_package

   .. autoclass:: Package

   .. autoclass:: PackageException

   .. autofunction:: PackageValidationError


Pblog extension
---------------

Storage
~~~~~~~

.. automodule:: flask_pblog.storage
   :members:



.. automodule:: flask_pblog.views

   Views
   ~~~~~
   The following routes are defined within Pblog:

   .. autofunction:: posts_list

   .. autofunction:: list_posts_in_topic

   .. autofunction:: show_post

   .. autofunction:: show_404
