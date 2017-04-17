from flask import abort
from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import url_for
from flask import Response
from sqlalchemy.orm.exc import NoResultFound


blueprint = Blueprint('blog', __name__, template_folder='templates')


@blueprint.route('/')
def posts_list():
    """Show a list of all posts and topics.

    Displays the ``pblog/posts-list.html`` template with the following context:
        posts: a list of ``pblog.models.Post`` instances
        categories: a list of all ``pblog.models.Category`` that have posts linked to them.
    """
    storage = current_app.extensions['pblog'].storage
    posts = storage.get_all_posts()
    topics = storage.get_all_topics()
    return render_template(
        'pblog/posts-list.html',
        posts=posts,
        topics=topics)


@blueprint.route('/topic/<topic_id>/<slug>')
def list_posts_in_topic(topic_id, slug):
    """Displays all posts in a given topic.

    If the topic does not exist or if no posts are associated with it, a
    404 response will be returned.

    If the topic exists but the slug is not the one provided in the url,
    a permanent redirection will be triggered to the correct url.

    Displays the ``pblog/post.html`` template with the following context:
        post: a ``pblog.models.Post`` instance.
        categories: a list of all ``pblog.models.Category`` that have posts linked to them.

    Args:
        topic_id (int): id of the Category to fetch post for
        slug (string): slug of the topic
    """
    storage = current_app.extensions['pblog'].storage

    try:
        topic = storage.get_topic(topic_id)
    except NoResultFound:
        abort(404)

    if topic.slug != slug:
        return redirect(
            url_for('blog.list_posts_in_topic',
                    topic_id=topic.id,
                    slug=topic.slug),
            code=301)
    posts = storage.get_posts_in_topic(topic_id)

    return render_template(
        'pblog/posts-list.html',
        posts=posts,
        topics=storage.get_all_topics())


@blueprint.route('/post/<post_id>/<slug>.md', defaults={'is_markdown': True})
@blueprint.route('/post/<post_id>/<slug>', defaults={'is_markdown': False})
def show_post(post_id, slug, is_markdown):
    """Displays a post given by its *id* and *slug*.

    If the slug does not match the actual slug stored in the database, a
    permanent redirect to a correct url that matches the slug.

    If the post does not exists, a 404 response will be returned.

    Displays the ``pblog/post.html`` template with the following context:
        post: a ``pblog.models.Post`` instance.
        categories: a list of all ``pblog.models.Category`` that have posts linked to them.

    Args:
        post_id (str): unique identifier of the post
        slug (str): slug of the post. Not required to match the actual slug
            stored in database
        is_markdown (bool): If True, will display the markdown content of the
            post. If False, will display the HTML rendered version
    """
    storage = current_app.extensions['pblog'].storage
    topics = storage.get_all_topics()
    try:
        post = storage.get_post(post_id)
    except NoResultFound:
        abort(404)

    # if the slug don't match, permanently redirect to correct url
    if post.slug != slug:
        return redirect(
            url_for('blog.show_post',
                    post_id=post.id,
                    slug=post.slug,
                    is_markdown=is_markdown),
            code=301)

    if is_markdown:
        return Response(post.md_content, mimetype='text/plain')
    return render_template('pblog/post.html', post=post, topics=topics)


@blueprint.app_errorhandler(404)
def show_404(err):
    """Displays the default 404 page.

    The template is ``pblog.404.html`` and have the following context:
        categories: a list of all ``pblog.models.Category`` that have posts linked to them.
    """
    topics = current_app.extensions['pblog'].storage.get_all_topics()
    return render_template('pblog/404.html', topics=topics), err.code
