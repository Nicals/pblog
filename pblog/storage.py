"""This module handles post generation
"""

from collections import namedtuple
from datetime import date

from cerberus import Validator
import markdown
from sqlalchemy.orm.exc import NoResultFound
import yaml

from pblog.core import db
from pblog.models import Category, Post


__all__ = [
    'PostError',
    'create_post',
    'update_post',
    'get_all_posts',
    'get_post']


class PostError(Exception):
    """Raised when building a post is impossible

    Attributes:
        errors (dict): A dictionary mapping field name to a list of errors.
    """
    def __init__(self, message, errors):
        self.errors = errors
        super().__init__(message)


PostDefinition = namedtuple('PostDefinition', (
    'title', 'slug', 'summary', 'date', 'category', 'markdown', 'html'))


def parse_markdown(md_file, encoding):
    """Extract and validates all post data from a markdown file.

    Args:
        md_file (file): The file to parse.
        encoding (str): The encoding used in the file.

    Returns:
        PostDefinition: The data extracted from the file

    Raises:
        PostError: If any data fails to correctly validate
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


def get_or_create_category(name):
    """Try to retrieve a category by its name.
    If it does not exist, a new category instance will be returned.

    The new category will not be persisted in database if created.

    Args:
        name (str): The name of the category to fetch.

    Returns:
        pblog.models.Category: The new category
    """
    try:
        return Category.query.filter_by(name=name).one()
    except NoResultFound:
        return Category(name=name)


def create_post(md_file, encoding='utf-8'):
    """Creates a new post from a markdown file and saves it in the database.

    Args:
        md_file (file): The file to build a new post from
        encoding (str): The encoding used in the markdown file.

    Returns:
        pblog.models.Post: The created post.

    Raises:
        PostError: If any of the data fails to validate
    """
    post_definition = parse_markdown(md_file, encoding)

    post = Post(
        title=post_definition.title,
        slug=post_definition.slug,
        summary=post_definition.summary,
        category=get_or_create_category(post_definition.category),
        md_content=post_definition.markdown,
        html_content=post_definition.html)

    db.session.add(post)
    db.session.commit()

    return post


def update_post(post, md_file, encoding='utf-8'):
    """Updates a post from a markdown file and saves it in the database.

    Ags:
        post (pblog.models.Post): The post to update
        md_file (file): The markdown file to update the post from
        encoding (str): The encoding used in the file

    Raises:
        pblog.storage.PostError: If any data fails to validate.
    """
    post_definition = parse_markdown(md_file, encoding)

    post.title = post_definition.title
    post.slug = post_definition.slug
    post.summary = post_definition.summary
    post.category = get_or_create_category(post_definition.category)
    post.md_content = post_definition.markdown
    post.html_content = post_definition.html

    db.session.add(post)
    db.session.commit()


def get_all_posts():
    """Get all stored posts.

    Returns:
        list of pblog.models.Post:
    """
    return Post.query.all()


def get_post(post_id):
    """Get a post by its id.

    Args:
        post_id: Unique identifier of the post to fetch

    Raises:
        sqlalchemy.orm.exc.NoResultFound: If no post exists with this id

    Returns:
        pblog.models.Post: The fetched post
    """
    return Post.query.filter_by(id=post_id).one()


def get_all_categories():
    """Returns all categories which have at least one associated post

    Returns:
        list of pblog.models.Category:
    """
    return Category.query.join(Post).all()
