Customize your blog
===================


Templates
---------

Templates can be ovrriden by providing a ``PBLOG_TEMPLATE_FOLDER`` settings.
The value is the path to a directory to take templates from insteand of using
Pblog defaults one.

Check the :mod:`~flask_pblog.views` module for more information on views.


Markdown
--------

PBlog uses `python-markdown <https://pypi.python.org/pypi/Markdown>`_ to parse
blog posts.

Without any configuration, a ``Markdown`` instance with minimal configuration
is used internally.
This markdown have the following `extensions <https://github.com/Nicals/markdown-extra>`_ enabled:

   + MetaExtension
   + SummaryExtension

You can provide a custom markdown instance to PBlog.
There is no need to explicitly register the MetaExtension et SummaryExtension as they
will be automatically provided if missing.

.. code:: python

   from flask import Flask
   from flask_pblog import PBlog
   from markdown import Markdown

   app = Flask(__name__)
   md = Markdown(
      extensions=['markdown.extensions.codehilite'],
      output_format='html5',
      tab_length=2,
   )
   storage = None  # build it as you whish
   PBlog(app, storage=storage, markdown=markdown)
