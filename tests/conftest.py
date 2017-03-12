import pytest
import os

from pblog.core import db as _db
from pblog.models import *  # NOQA
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
def db(app, request):
    _db.create_all()
    yield _db
    _db.drop_all()
