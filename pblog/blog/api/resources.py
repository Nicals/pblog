from flask import abort
from flask_restful import Resource
from flask_restful import reqparse
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from pblog.core import api
from pblog.core import db
from pblog.models import Post
from pblog.posts import create_post
from pblog.posts import update_post
from pblog.posts import PostError
from pblog.schemas import PostSchema


__all__ = ['PostResource', 'PostListResource']


def build_edit_post_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(
        'encoding',
        default='utf-8',
        help="Encoding of the markdown file content. Defaults to utfg-8")
    parser.add_argument(
        'post',
        type=FileStorage,
        location='files')

    return parser


@api.resource('/posts')
class PostListResource(Resource):
    def post(self):
        """Creates a new post

        The request must have the following parameters:
            + encoding: optional encoding for the markdown file. Defaults to utf-8
            + markdown: a file containing the markdown paper

        On successful post creation, the response will return an HTTP 201
        response with the created post.

        Any error will be returned with the HTTP 400 response. Errors will be
        stored in an "errors" dictionary.
        """
        parser = build_edit_post_parser()
        args = parser.parse_args()

        try:
            post = create_post(args.post, args.encoding)
        except PostError as e:
            return dict(errors=e.errors), 400

        db.session.add(post)
        db.session.commit()

        post_schema = PostSchema()
        return post_schema.dump(post).data, 201


@api.resource('/posts/<int:post_id>')
class PostResource(Resource):
    def post(self, post_id):
        """Update an existing post

        On success, return a 200 OK response.

        Any error will be returned with the HTTP 400 response. Errors will be
        stored in an "errors" dictionary.

        A 404 will be returned if the updated post does not exist.
        """
        try:
            post = Post.query.filter_by(id=post_id).one()
        except NoResultFound:
            abort(404, errors={'post': ["The post with id {} does not exist".format(post_id)]})

        parser = build_edit_post_parser()
        args = parser.parse_args()

        try:
            update_post(post, args.post, args.encoding)
        except PostError as e:
            return dict(errors=e.errors), 400

        db.session.add(post)
        db.session.commit()

        post_schema = PostSchema()
        return post_schema.dump(post).data
