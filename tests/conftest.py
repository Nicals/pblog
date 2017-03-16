from datetime import date
import os

import pytest

from pblog.core import db as _db
from pblog.models import Post, Category
from pblog.factory import create_app


SETTINGS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.py')


@pytest.fixture(scope='session')
def app(request):
    """Session wide test flask application
    """
    os.environ['PBLOG_SETTINGS'] = SETTINGS_PATH
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def client(app):
    yield app.test_client()


@pytest.fixture(scope='function')
def db(app, request):
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope='function')
def post(db):
    post = Post(
        title='A post',
        slug='a-post',
        summary='this is a post',
        published_date=date(2010, 1, 1),
        category=Category(name='Category', slug='category'),
        md_content='markdown', html_content='<h1>markdown</h1')
    db.session.add(post)
    db.session.commit()

    yield post
