B-Blog
======

A command line blog using markdown syntax.

Installation
------------

To build the database:

```python
from pblog.factory import create_app
from pblog.core import db
from pblog.models import *

app = create_app(__name__, '')
with app.app_context():
  db.create_all()
```

Configuration
-------------

Default configuration can be overriden by providing the path of a settings
file in an **PBLOG_SETTINGS** environment variable.

| Key | Type | Comments |
| --- | ---- | -------- |
| DEBUG | bool | defaults to False |
| SECRET_KEY | string | default to an insecure value |
| SQLALCHEMY_DATABASE_URI | string | |
| PBLOG_CONTRIBUTORS | dict | A dictionnary mapping usernames to hashed passwords. See **commands** to generate passwords. |


Posts
-----

Posts are markdown file with yaml headers.

```markdown
---
id: 12
title: The title of the post
slug: a slug to use as a url
category: A category
date: 2017-02-06
---

[summary]
An optional summmary paragraph.

The post content goes here.
```


| Header | Type | Comments |
| ------ | ---- | -------- |
| id | int | used client side to update existing posts |
| title | string | |
| slug | string | unique slug |
| category | string | |
| date | date | current date if not set |
