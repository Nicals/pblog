from flask import abort
from flask import Blueprint
from flask import render_template
from sqlalchemy.orm.exc import NoResultFound

from pblog.models import Post


blueprint = Blueprint('blog', __name__)


@blueprint.route('/')
def home_page():
    posts = Post.query.all()
    return render_template(
        'posts-list.html',
        posts=posts)


@blueprint.route('/post/<slug>')
def show_post(slug):
    try:
        post = Post.query.filter_by(slug=slug).one()
    except NoResultFound:
        abort(404)

    return render_template('post.html', post=post)


@blueprint.app_errorhandler(404)
def show_404(err):
    return render_template('404.html')
