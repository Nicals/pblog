from datetime import date

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytest

from flask_pblog.models import Base, Post, Category
from flask_pblog.storage import Storage
from flask_pblog import PBlog


@pytest.fixture(scope='function')
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'sqlite://'
    app.config['TESTING'] = True
    db = SQLAlchemy(app)
    storage = Storage(db.session)
    PBlog(app, storage=storage)

    Base.metadata.create_all(db.engine)
    with app.app_context():
        yield app
    Base.metadata.drop_all(db.engine)


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def storage(app):
    return app.extensions['pblog'].storage


@pytest.fixture(scope='function')
def post(storage):
    post = Post(
        title='A post',
        slug='a-post',
        summary='this is a post',
        published_date=date(2010, 1, 1),
        category=Category(name='Category', slug='category'),
        md_content='markdown', html_content='<h1>markdown</h1')
    storage.session.add(post)
    storage.session.commit()

    return post
