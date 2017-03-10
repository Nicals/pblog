"""This module handles post generation
"""

from sqlalchemy.orm.exc import NoResultFound

from pblog.core import db
from pblog.models import Category, Post
from pblog.markdown import parse_markdown


__all__ = [
    'create_post',
    'update_post',
    'get_all_posts',
    'get_post']


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
