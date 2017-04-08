Markdown Posts
==============

Posts are written in `markdown <https://daringfireball.net/projects/markdown/>`_.

Some metadata are required to configure some post.


============== ======= ==============================================================

id             dict    a dctionary mapping environment names to actual post id in
                       the web interface. Not required for new post.
title          string  the title of this post. Required.
slug           string  a slug to use for this post. It is not required to be a unique
                       value. Not required.
category       string  name of the category for this post. If not already existing,
                       a new category will be created in the web interface. Required.
published_date date    yyyy-mm-dd. If not set, the current date will be set to
                       the current date.

============== ======= ==============================================================

A ``[summary]`` tag can be placed on top of a paragraph to use it for displaying
the post on the front page.
If no summary is given, the first paragraph of the post will be used.

No title should be set.
The ``title`` tag of the metadata will be inserted in the converted HTML.

For example:

.. code-block:: text

   ---
   id:
       testing: 12
       prod: 4
   title: My first blog post
   slug: my-first-blog-post
   category: Blogging
   ---

   [Summary]
   This is my first post.

   Hello blogging world.

When a paper is published, some metadata may be automatically inserted in the
local markdown file.

When a post is published and has no id, a new post will be created on the web
interface.
The id part of the local markdown file will be automatically updated to
reflect the web interface db id.

If the ``slug`` is not set in the metadata, it will be generated from the ``title``.

If the ``date`` metadata is not given, it will be automatically set as the
current date when publishing the post.


Local resources
---------------

In post, any image or link with a relative url will be associated with a file
you must provide within the post directory.
For example, considering the following post:

.. code-block:: text

   Have a look to this awesome kitten image:

   ![A kitten](https://http.cat/200)

   [a kitten stylesheet](/static/kitten.css)

   ![A better kitten](a-kitten.jpg)

   Find better kitten [here][files/kitten.tar.gz]

Here, the first two links will be kept as it.
They are considered external from from the post.

The last two links are relative to the post path.
Your file structure must be the following:

.. code-block:: text

   my-post.md
   a-kitten.jpg
   files/kitten.tar.gz

When published, all this relative path will be fetched and sent to the blog
server.

They will be stored in a directory given by the `PBLOG_RESOURCES_PATH` settings
and served from the `PBLOG_RESOURCE_URL` url.

A directory named after the blog slug is created in the root resource path to
store post resources.
