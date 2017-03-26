API
===

Pblog
-----

Markdown
~~~~~~~~

.. automodule:: pblog.markdown

   .. autoclass:: PostError

   .. autofunction:: update_meta

   .. autofunction:: parse_markdown


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

   .. autofunction:: list_posts_in_category

   .. autofunction:: show_post

   .. autofunction:: show_404
