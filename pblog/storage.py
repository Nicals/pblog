"""This module handles post generation
"""

from collections import namedtuple
from datetime import date

from cerberus import Validator
import markdown
from sqlalchemy.orm.exc import NoResultFound
import yaml

from pblog.models import Category, Post


__all__ = ['PostError', 'create_post']


class PostError(Exception):
    """Raised when building a post is impossible
    """
    def __init__(self, message, errors):
        self.errors = errors
        super().__init__(message)


PostDefinition = namedtuple('PostDefinition', (
    'title', 'slug', 'summary', 'date', 'category', 'markdown', 'html'))


def parse_markdown(md_file, encoding, post=None):
    """
    :param string md_content: markdown content to parse
    :param pblog.models.Post post: an existing post if the markdown file is
        parsed for update

    :raises PostError: if some data failed to validate

    :return PostDefinition:
    """
    md = markdown.Markdown(extensions=['pblog.markdown.extensions.summary',
                                       'pblog.markdown.extensions.meta'])

    try:
        md_content = md_file.read().decode(encoding)
    except UnicodeDecodeError:
        raise PostError(
            "Markdown file is not {} compatible".format(encoding),
            errors={'encoding': ["document could not be interpreted with {}".format(encoding)]})
    except LookupError:
        raise PostError(
            "Encoding {} is not valid".format(encoding),
            errors={'encoding': ["unknown encoding {}".format(encoding)]})

    try:
        html_content = md.convert(md_content)
    except yaml.YAMLError:
        raise PostError(
            "meta is not valid yaml",
            errors={'markdown': ["could not parse header"]})

    validator = Validator({
        'title': {'type': 'string', 'required': True},
        'slug': {'type': 'string', 'required': True, 'regex': '^[A-Za-z0-9_-]+$'},
        'category': {'type': 'string', 'required': True},
        'date': {'type': 'date'},
    })

    if not validator.validate(md.meta):
        raise PostError("Meta data did not validate", errors=validator.errors)

    return PostDefinition(
        title=md.meta['title'],
        slug=md.meta['slug'],
        summary=md.summary,
        date=md.meta.get('date', date.today()),
        category=md.meta['category'],
        markdown=md_content,
        html=html_content)


def create_post(md_file, encoding='utf-8'):
    """
    :param file md_file:
    :param string encoding:

    :raises PostError: if some data fails to validate

    :return created post:
    """
    post_definition = parse_markdown(md_file, encoding)

    # get or create a category
    try:
        category = Category.query.filter_by(name=post_definition.category).one()
    except NoResultFound:
        category = Category(name=post_definition.category)

    return Post(
        title=post_definition.title,
        slug=post_definition.slug,
        summary=post_definition.summary,
        category=category,
        md_content=post_definition.markdown,
        html_content=post_definition.html)


def update_post(post, md_file, encoding='utf-8'):
    """
    :param pblog.models.Post post:
    :param file md_file:
    :param string encoding:

    :raises PostError: if some data fails to validate
    """
    post_definition = parse_markdown(md_file, encoding, post)

    # get or create a category if needed
    if post.category.name != post_definition.category:
        try:
            post.category = Category.query.filter_by(name=post_definition.category).one()
        except NoResultFound:
            post.category = Category(name=post_definition.category)

    post.title = post_definition.title
    post.slug = post_definition.slug
    post.summary = post_definition.summary
    post.md_content = post_definition.markdown
    post.html_content = post_definition.html
