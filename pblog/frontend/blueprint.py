from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for
from flask import Response
from sqlalchemy.orm.exc import NoResultFound

from pblog import storage


blueprint = Blueprint('blog', __name__, template_folder='templates')


@blueprint.route('/')
def post_lists():
    posts = storage.get_all_posts()
    categories = storage.get_all_categories()
    return render_template(
        'posts-list.html',
        posts=posts,
        categories=categories)


@blueprint.route('/post/<post_id>/<slug>', defaults={'is_markdown': False})
@blueprint.route('/post/<post_id>/<slug>.md', defaults={'is_markdown': True})
def show_post(post_id, slug, is_markdown):
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
    return render_template('post.html', post=post)


@blueprint.app_errorhandler(404)
def show_404(err):
    return render_template('404.html')
