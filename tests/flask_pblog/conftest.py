from datetime import date
from io import BytesIO
import tarfile

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from markdown import Markdown
import pytest

from flask_pblog.models import Base, Post, Topic
from flask_pblog.storage import Storage
from flask_pblog import PBlog


@pytest.fixture(scope='function')
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'sqlite://'
    app.config['PBLOG_RESOURCES_PATH'] = ''
    app.config['PBLOG_RESOURCES_URL'] = ''
    app.config['TESTING'] = True
    db = SQLAlchemy(app)
    markdown = Markdown(extensions=['markdown_extra.resource_path'])
    storage = Storage(db.session)
    PBlog(app, storage=storage, markdown=markdown)

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
        topic=Topic(name='Topic', slug='topic'),
        md_content='markdown', html_content='<h1>markdown</h1')
    storage.session.add(post)
    storage.session.commit()

    return post


@pytest.fixture(scope='function')
def post_package():
    """This fixture provides a packaged post
    """
    package_file = BytesIO()
    with tarfile.open(mode='w', fileobj=package_file) as tar:
        # metadata
        meta_content = b'encoding: utf-8\npost: post.md'
        file_info = tarfile.TarInfo('package.yml')
        file_info.size = len(meta_content)
        tar.addfile(file_info, BytesIO(meta_content))

        # post
        post_content = b'''---
title: A title
topic: A topic
---

[summary]
A summary

A paragraph
'''
        file_info = tarfile.TarInfo('post.md')
        file_info.size = len(post_content)
        tar.addfile(file_info, BytesIO(post_content))
    package_file.seek(0)

    return package_file
