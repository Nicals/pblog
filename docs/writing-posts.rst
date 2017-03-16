Markdown Posts
==============

Posts are written in `markdown <https://daringfireball.net/projects/markdown/>`_.

Some metadata are required to configure some post.

======== ======= ==============================================================

id       integer id of this post in the web interface. If null or not set,
                 publishing this file will create a new post. If not null, an
                 existing post will be created
title    string  the title of this post
slug     string  a slug to use for this post. It is not required to be a unique
                 value
category string  name of the category for this post. If not already existing,
                 a new category will be created in the web interface.
date     date    yyyy-mm-dd. If not set, the current date will be inserted.

======== ======= ==============================================================

A ``[summary]`` tag can be placed on top of a paragraph to use it for displaying
the post on the front page.
If no summary is given, the first paragraph of the post will be used.

No title should be set.
The ``title`` tag of the metadata will be inserted in the converted HTML.

For example:

.. code-block:: text

   ---
   title: My first blog post
   slug: my-first-blog-post
   category: Blogging
   ---

   [Summary]
   This is my first post.

   Hello blogging world.
