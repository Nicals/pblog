"""This module handles post generation
"""

from sqlalchemy.orm.exc import NoResultFound
from slugify import slugify

from flask_pblog.models import Topic, Post


class Storage:
    """This class implements database access through SQLAlchemy
    """
    def __init__(self, session):
        """
        Args:
            session (sqlalchemy.orm.session.Session): session to use to
                access the database
        """
        self.session = session

    def get_or_create_topic(self, name):
        """Try to retrieve a topic by its name.
        If it does not exist, a new topic instance will be returned.

        The new topic will not be persisted in database if created.

        Args:
            name (str): The name of the topic to fetch.

        Returns:
            flask_pblog.models.Topic: The new topic
        """
        try:
            return self.session.query(Topic).filter_by(name=name).one()
        except NoResultFound:
            return Topic(name=name, slug=slugify(name))

    def create_post(self, post_package):
        """Creates a new post from a markdown file and saves it in the database.

        Args:
            post_package (pblog.package.Package): Post package definition
                to build a new post from.

        Returns:
            flask_pblog.models.Post: The created post.
        """
        post = Post(
            title=post_package.post_title,
            slug=post_package.post_slug,
            published_date=post_package.published_date,
            summary=post_package.summary,
            topic=self.get_or_create_topic(post_package.topic_name),
            md_content=post_package.markdown_content,
            html_content=post_package.html_content)

        self.session.add(post)
        self.session.commit()

        return post

    def update_post(self, post, post_package):
        """Updates a post from a markdown file and saves it in the database.

        Args:
            post (flask_pblog.models.Post): The post to update
            md_package (pblog.package.Package): Post package definition to
                update post from.
        """
        post.title = post_package.post_title
        post.slug = post_package.post_slug
        post.published_date = post_package.published_date
        post.summary = post_package.summary
        post.topic = self.get_or_create_topic(post_package.topic_name)
        post.md_content = post_package.markdown_content
        post.html_content = post_package.html_content

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

    def get_topic(self, topic_id):
        """Get a topic by its id that have at least one associated post.

        Args:
            topic_id: Unique identifier of the topic to fetch

        Raises:
            sqlalchemy.orm.exc.NoResultFound: If no categories exists with
                this id or if a topic was found without any associated
                posts.

        Returns:
            flask_pblog.models.Topic: The fetched topic
        """
        return self.session.query(Topic).filter_by(id=topic_id).join(Post).one()

    def get_all_topics(self):
        """Returns all topics which have at least one associated post

        Returns:
            list of flask_pblog.models.Topic:
        """
        return self.session.query(Topic).join(Post).all()

    def get_posts_in_topic(self, topic_id):
        """Get all posts belonging to a given topic.

        Args:
            topic_id: Unique identifier of the topic to filter by

        Returns:
            list of flask_pblgo.models.Post: Filtered posts
        """
        return self.session.query(Post).filter_by(topic_id=topic_id).all()

    def save_resources(self, root_path, post_package):
        """Save some resurces on disk

        Args:
            root_path: pathlib.Path: base path to store resources
            post_package (pblog.package.Package):
        """
        for resource in post_package.resources:
            resource.save(root_path, post_package.post_slug)
