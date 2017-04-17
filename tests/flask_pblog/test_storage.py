from datetime import date

import pytest
from sqlalchemy.orm.exc import NoResultFound

from pblog.package import Package
from flask_pblog import models


def test_create_topic_if_not_existing(storage):
    topic = storage.get_or_create_topic("Topic")

    assert topic.id is None
    assert topic.name == 'Topic'
    assert topic.slug == 'topic'


def test_create_post(storage):
    post_definition = Package(
        post_title='Title', post_slug='slug', summary='summary',
        published_date=date(2017, 3, 12),
        topic_name='Topic', markdown_content='markdown')
    post_definition._html_content = 'html'

    post = storage.create_post(post_definition)

    assert post.title == 'Title'
    assert post.slug == 'slug'
    assert post.summary == 'summary'
    assert post.published_date == date(2017, 3, 12)
    assert post.topic.name == 'Topic'
    assert post.md_content == 'markdown'
    assert post.html_content == 'html'


def test_update_post(storage):
    post_definition = Package(
        post_id=2, post_title='Title', post_slug='slug', summary='summary',
        published_date=date(2017, 3, 12), topic_name='Topic',
        markdown_content='markdown')
    post_definition._html_content = 'html'
    post = models.Post(
        title='old', slug='old', summary='summary',
        published_date=date(2010, 1, 2),
        topic=models.Topic(name='Old topic', slug='ot'), md_content='m',
        html_content='h')
    storage.session.add(post)
    storage.session.commit()

    storage.update_post(post, post_definition)

    new_post = storage.session.query(models.Post).filter_by(id=post.id).one()
    assert new_post.title == 'Title'
    assert new_post.slug == 'slug'
    assert new_post.summary == 'summary'
    assert new_post.published_date == date(2017, 3, 12)
    assert new_post.topic.name == 'Topic'
    assert new_post.md_content == 'markdown'
    assert new_post.html_content == 'html'


def test_get_existing_topic(storage):
    storage.session.add(models.Topic(name='Topic', slug='topic'))
    storage.session.commit()

    topic = storage.get_or_create_topic('Topic')
    assert topic.id is not None
    assert topic.name == 'Topic'


def test_get_post(storage):
    post = models.Post(
        title='Title', slug='slug',
        topic=models.Topic(name='Topic', slug='topic'),
        published_date=date(2017, 3, 1), md_content='m', html_content='h')
    storage.session.add(post)
    storage.session.commit()

    assert storage.get_post(post.id) == post


def test_get_all_topics(storage):
    topic = models.Topic(name='Topic', slug='topic')
    storage.session.add(models.Post(
        title='Title', slug='slug', topic=topic, summary='',
        md_content='m',
        html_content='h', published_date=date(2017, 3, 13)))
    storage.session.add(models.Topic(name='foo', slug='c'))
    storage.session.commit()

    assert storage.get_all_topics() == [topic]


def test_get_posts_in_topic(storage):
    topic = models.Topic(name='Topic', slug='topic')
    post = models.Post(
        title="In Topic", slug="it", summary='', md_content='m',
        html_content='h', published_date=date(2017, 3, 12), topic=topic)
    other_post = models.Post(
        title="Out of Category", slug="ooc", summary='', md_content='m',
        html_content='h', published_date=date(2017, 3, 12),
        topic=models.Topic(name='Other topic', slug='ot'))
    storage.session.add(post)
    storage.session.add(other_post)
    storage.session.commit()

    assert storage.get_posts_in_topic(topic.id) == [post]


def test_get_not_existing_topic(storage):
    with pytest.raises(NoResultFound):
        storage.get_topic(1)


def test_topic_without_posts(storage):
    topic = models.Topic(name='Foo', slug='foo')
    storage.session.add(topic)
    storage.session.commit()

    with pytest.raises(NoResultFound):
        storage.get_topic(topic.id)


def test_get_topic(storage, post):
    assert storage.get_topic(post.topic.id) == post.topic
