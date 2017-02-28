from functools import wraps

from flask import abort
from flask import current_app
from flask_restful import Resource
from flask_restful import reqparse
import itsdangerous
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from pblog.core import api
from pblog.models import Post
from pblog.storage import create_post
from pblog.storage import update_post
from pblog.storage import PostError
from pblog import security
from pblog.schemas import PostSchema


__all__ = ['PostResource', 'PostListResource']


def auth_required(func):
    """Will abort with:

    400 if no token is provided
    401 if the token is invalid.
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'X-Pblog-Token',
            dest='token',
            required=True,
            location='headers')
        args = parser.parse_args()

        try:
            security.validate_token(
                args.token,
                current_app.config['SECRET_KEY'],
                max_age=300)
        except itsdangerous.SignatureExpired:
            return dict(errors={'auth': ["Signature expired"]}), 401
        except itsdangerous.BadSignature:
            return dict(errors={'auth': ["Bad signature"]}), 401
        except itsdangerous.BadTimeSignature:
            return dict(errors={'auth': ["Signature does not match"]}), 401

        return func(*args, **kwargs)

    return decorator


def build_edit_post_parser():
    parser = reqparse.RequestParser()
    parser.add_argument(
        'encoding',
        default='utf-8',
        help="Encoding of the markdown file content. Defaults to utfg-8")
    parser.add_argument(
        'post',
        type=FileStorage,
        required=True,
        location='files')

    return parser


@api.resource('/auth')
class AuthResource(Resource):
    def post(self):
        """
        Returns a 400 response if the request is not correct.

        Returns a 200 response with a token if the user is logged.

        Returns a 401 response if auth fails.
        """
        parser = reqparse.RequestParser()
        parser.add_argument(
            'username',
            required=True)
        parser.add_argument(
            'password',
            required=True)
        args = parser.parse_args()

        try:
            hashed_password = current_app.config['PBLOG_CONTRIBUTORS'][args.username]
        except KeyError:
            abort(401)
        else:
            if not security.check_password(args.password, hashed_password):
                abort(401)

        token = security.generate_token(args.username, current_app.config['SECRET_KEY'])

        return {'token': token.decode('utf-8')}, 200


@api.resource('/posts')
class PostListResource(Resource):
    @auth_required
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

        post_schema = PostSchema()
        return post_schema.dump(post).data, 201


@api.resource('/posts/<int:post_id>')
class PostResource(Resource):
    @auth_required
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

        post_schema = PostSchema()
        return post_schema.dump(post).data
