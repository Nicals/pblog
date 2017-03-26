"""This module handles post generation
"""

from sqlalchemy.orm.exc import NoResultFound
from slugify import slugify

from flask_pblog.models import Category, Post


class Storage:
    """This class implements database access through SQLAlchemy
    """
    def __init__(self, session):
        """
        Args:
            session (sqlalchemy.orm.session.Session): session to use to
                access the database
            markdown (markdown.Markdown): the markdown instance to use to
                convert posts.
        """
        self.session = session

    def get_or_create_category(self, name):
        """Try to retrieve a category by its name.
        If it does not exist, a new category instance will be returned.

        The new category will not be persisted in database if created.

        Args:
            name (str): The name of the category to fetch.

        Returns:
            flask_pblog.models.Category: The new category
        """
        try:
            return self.session.query(Category).filter_by(name=name).one()
        except NoResultFound:
            return Category(name=name, slug=slugify(name))

    def create_post(self, post_definition):
        """Creates a new post from a markdown file and saves it in the database.

        Args:
            md_file (file): The file to build a new post from
            encoding (str): The encoding used in the markdown file.

        Returns:
            flask_pblog.models.Post: The created post.

        Raises:
            pblog.markdown.PostError: If any of the data fails to validate
        """
        post = Post(
            title=post_definition.title,
            slug=post_definition.slug,
            published_date=post_definition.date,
            summary=post_definition.summary,
            category=self.get_or_create_category(post_definition.category),
            md_content=post_definition.markdown,
            html_content=post_definition.html)

        self.session.add(post)
        self.session.commit()

        return post

    def update_post(self, post, post_definition):
        """Updates a post from a markdown file and saves it in the database.

        Ags:
            post (flask_pblog.models.Post): The post to update
            md_file (file): The markdown file to update the post from
            encoding (str): The encoding used in the file

        Raises:
            pblog.markdown.PostError: If any data fails to validate.
        """
        post.title = post_definition.title
        post.slug = post_definition.slug
        post.published_date = post_definition.date
        post.summary = post_definition.summary
        post.category = self.get_or_create_category(post_definition.category)
        post.md_content = post_definition.markdown
        post.html_content = post_definition.html

        self.session.add(post)
        self.session.commit()

    def get_all_posts(self):
        """Get all stored posts.

        Returns:
            list of flask_pblog.models.Post:
        """
        return self.session.query(Post).all()

    def get_post(self, post_id):
        """Get a post by its id.

        Args:
            post_id: Unique identifier of the post to fetch

        Raises:
            sqlalchemy.orm.exc.NoResultFound: If no post exists with this id

        Returns:
            flask_pblog.models.Post: The fetched post
        """
        return self.session.query(Post).filter_by(id=post_id).one()

    def get_category(self, category_id):
        """Get a category by its id that have at least one associated post.

        Args:
            category_id: Unique identifier of the category to fetch

        Raises:
            sqlalchemy.orm.exc.NoResultFound: If no categories exists with
                this id or if a category was found without any associated
                posts.

        Returns:
            flask_pblog.models.Category: The fetched category
        """
        return self.session.query(Category).filter_by(id=category_id).join(Post).one()

    def get_all_categories(self):
        """Returns all categories which have at least one associated post

        Returns:
            list of flask_pblog.models.Category:
        """
        return self.session.query(Category).join(Post).all()

    def get_posts_in_category(self, category_id):
        """Get all posts belonging to a given category.

        Args:
            category_id: Unique identifier of the category to filter by

        Returns:
            list of flask_pblgo.models.Post: Filtered posts
        """
        return self.session.query(Post).filter_by(category_id=category_id).all()
