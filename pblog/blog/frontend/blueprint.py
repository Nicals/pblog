from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for
from sqlalchemy.orm.exc import NoResultFound

from pblog import storage


blueprint = Blueprint('blog', __name__)


@blueprint.route('/')
def home_page():
    posts = storage.get_all_posts()
    return render_template(
        'posts-list.html',
        posts=posts)


@blueprint.route('/post/<post_id>/<slug>')
def show_post(post_id, slug):
    try:
        post = storage.get_post(post_id)
    except NoResultFound:
        abort(404)

    # if the slug don't match, permanently redirect to correct url
    if post.slug != slug:
        return redirect(url_for('blog.show_post', post_id=post.id, slug=post.slug), code=301)

    return render_template('post.html', post=post)


@blueprint.app_errorhandler(404)
def show_404(err):
    return render_template('404.html')
