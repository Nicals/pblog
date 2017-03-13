from datetime import date
from unittest.mock import Mock, patch

from pblog.markdown import PostDefinition
from pblog import storage
from pblog import models


def test_create_category_if_not_existing(db):
    category = storage.get_or_create_category("Category")

    assert category.id is None
    assert category.name == 'Category'
    assert category.slug == 'category'


@patch('pblog.storage.parse_markdown')
def test_create_post(parse_markdown, db):
    md_file = Mock()
    parse_markdown.return_value = PostDefinition(
        title='Title', slug='slug', summary='summary', date=date(2017, 3, 12),
        category='Category', markdown='markdown', html='html')

    post = storage.create_post(md_file, encoding='iso-8859-1')

    parse_markdown.assert_called_once_with(md_file, 'iso-8859-1')
    assert post.title == 'Title'
    assert post.slug == 'slug'
    assert post.summary == 'summary'
    assert post.published_date == date(2017, 3, 12)
    assert post.category.name == 'Category'
    assert post.md_content == 'markdown'
    assert post.html_content == 'html'


@patch('pblog.storage.parse_markdown')
def test_update_post(parse_markdown, db):
    md_file = Mock()
    parse_markdown.return_value = PostDefinition(
        title='Title', slug='slug', summary='summary',
        date=date(2017, 3, 12), category='Category',
        markdown='markdown', html='html')
    post = models.Post(
        title='old', slug='old', summary='summary',
        published_date=date(2010, 1, 2),
        category=models.Category(name='Old Category', slug='oc'), md_content='m',
        html_content='h')
    db.session.add(post)
    db.session.commit()

    storage.update_post(post, md_file, 'iso-8859-1')

    parse_markdown.assert_called_once_with(md_file, 'iso-8859-1')
    new_post = models.Post.query.filter_by(id=post.id).one()
    assert new_post.title == 'Title'
    assert new_post.slug == 'slug'
    assert new_post.summary == 'summary'
    assert new_post.published_date == date(2017, 3, 12)
    assert new_post.category.name == 'Category'
    assert new_post.md_content == 'markdown'
    assert new_post.html_content == 'html'


def test_get_existing_category(db):
    db.session.add(models.Category(name='Category', slug='cat'))
    db.session.commit()

    category = storage.get_or_create_category('Category')
    assert category.id is not None
    assert category.name == 'Category'


def test_get_post(db):
    post = models.Post(
        title='Title', slug='slug',
        category=models.Category(name='Category', slug='c'),
        published_date=date(2017, 3, 1), md_content='m', html_content='h')
    db.session.add(post)
    db.session.commit()

    assert storage.get_post(post.id) == post


def test_get_all_categories(db):
    category = models.Category(name='Category', slug='c')
    db.session.add(models.Post(
        title='Title', slug='slug', category=category, summary='',
        md_content='m',
        html_content='h', published_date=date(2017, 3, 13)))
    db.session.add(models.Category(name='foo', slug='c'))
    db.session.commit()

    assert storage.get_all_categories() == [category]
