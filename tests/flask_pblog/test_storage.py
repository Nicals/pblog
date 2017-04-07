from datetime import date

import pytest
from sqlalchemy.orm.exc import NoResultFound

from pblog.package import Package
from flask_pblog import models


def test_create_category_if_not_existing(storage):
    category = storage.get_or_create_category("Category")

    assert category.id is None
    assert category.name == 'Category'
    assert category.slug == 'category'


def test_create_post(storage):
    post_definition = Package(
        post_title='Title', post_slug='slug', summary='summary',
        published_date=date(2017, 3, 12),
        category_name='Category', markdown_content='markdown')
    post_definition._html_content = 'html'

    post = storage.create_post(post_definition)

    assert post.title == 'Title'
    assert post.slug == 'slug'
    assert post.summary == 'summary'
    assert post.published_date == date(2017, 3, 12)
    assert post.category.name == 'Category'
    assert post.md_content == 'markdown'
    assert post.html_content == 'html'


def test_update_post(storage):
    post_definition = Package(
        post_id=2, post_title='Title', post_slug='slug', summary='summary',
        published_date=date(2017, 3, 12), category_name='Category',
        markdown_content='markdown')
    post_definition._html_content = 'html'
    post = models.Post(
        title='old', slug='old', summary='summary',
        published_date=date(2010, 1, 2),
        category=models.Category(name='Old Category', slug='oc'), md_content='m',
        html_content='h')
    storage.session.add(post)
    storage.session.commit()

    storage.update_post(post, post_definition)

    new_post = storage.session.query(models.Post).filter_by(id=post.id).one()
    assert new_post.title == 'Title'
    assert new_post.slug == 'slug'
    assert new_post.summary == 'summary'
    assert new_post.published_date == date(2017, 3, 12)
    assert new_post.category.name == 'Category'
    assert new_post.md_content == 'markdown'
    assert new_post.html_content == 'html'


def test_get_existing_category(storage):
    storage.session.add(models.Category(name='Category', slug='cat'))
    storage.session.commit()

    category = storage.get_or_create_category('Category')
    assert category.id is not None
    assert category.name == 'Category'


def test_get_post(storage):
    post = models.Post(
        title='Title', slug='slug',
        category=models.Category(name='Category', slug='c'),
        published_date=date(2017, 3, 1), md_content='m', html_content='h')
    storage.session.add(post)
    storage.session.commit()

    assert storage.get_post(post.id) == post


def test_get_all_categories(storage):
    category = models.Category(name='Category', slug='c')
    storage.session.add(models.Post(
        title='Title', slug='slug', category=category, summary='',
        md_content='m',
        html_content='h', published_date=date(2017, 3, 13)))
    storage.session.add(models.Category(name='foo', slug='c'))
    storage.session.commit()

    assert storage.get_all_categories() == [category]


def test_get_posts_in_category(storage):
    category = models.Category(name='Category', slug='c')
    post = models.Post(
        title="In Category", slug="ic", summary='', md_content='m',
        html_content='h', published_date=date(2017, 3, 12), category=category)
    other_post = models.Post(
        title="Out of Category", slug="ooc", summary='', md_content='m',
        html_content='h', published_date=date(2017, 3, 12),
        category=models.Category(name='Other category', slug='oc'))
    storage.session.add(post)
    storage.session.add(other_post)
    storage.session.commit()

    assert storage.get_posts_in_category(category.id) == [post]


def test_get_not_existing_category(storage):
    with pytest.raises(NoResultFound):
        storage.get_category(1)


def test_category_without_posts(storage):
    category = models.Category(name='Foo', slug='foo')
    storage.session.add(category)
    storage.session.commit()

    with pytest.raises(NoResultFound):
        storage.get_category(category.id)


def test_get_category(storage, post):
    assert storage.get_category(post.category.id) == post.category
