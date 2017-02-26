B-Blog
======

A command line blog using markdown syntax.

Configuration
-------------

Default configuration can be overriden by providing the path of a settings
file in an **PBLOG_SETTINGS** environment variable.

| Key | Type | Comments |
| --- | ---- | -------- |
| DEBUG | bool | defaults to False |
| SECRET_KEY | string | default to an insecure value |
| SQLALCHEMY_DATABASE_URI | string | |


To build the database:

```python
from pblog.factory import create_app
from pblog.core import db
from pblog.models import *

app = create_app(__name__, '')
with app.app_context():
  db.create_all()
```
