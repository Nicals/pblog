"""This module contains web API resources used for Pblog management.

Resources called returns JSON response.

If a request is not well formatted, a 400 response will be return and a `message`
key will contain a string indicating why the request was not accepted.
Those message are aimed to the client using the API and should be dealt by it.

Example:
    {
        "message": "Missing 'post_id' field",
    }


If the request is valid (ie: all required data are correctly sent) but the
request content did not validate, a 400 is returned and field errors are
given in an `errors` field of the response.
This field is a dictionary mapping the field name to a list of string describing
the errors.
This case is usually because the user failed to provide correct data to the
client.

Example:
    {
        "errors": {
            "post_id": {"'foo' is not an integer"],
        },
    }
"""

from functools import wraps

from flask import abort
from flask import Blueprint
from flask import current_app
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse
import itsdangerous
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from flask_pblog import security
from flask_pblog.schemas import PostSchema
from pblog.package import read_package, PackageException, PackageValidationError


blueprint = Blueprint('api', __name__)
api = Api(blueprint)


def auth_required(func):
    """This decorator is used to ensure that a user is correctly authenticated
    before he can access a given resource.

    Authentication is checkeb by providing a valid token in X-Pblog-Token
    header key.

    If no token is provided or the token is not correctly formatted, a 401
    response will be return with the content:
            {"message": "invalid_token"}

    If the token has expired, a 401 response will be returne with the content:
            {"message": "token_expired"}
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'X-Pblog-Token',
            dest='token',
            required=False,
            location='headers')
        req_args = parser.parse_args()

        if req_args.token is None:
            return dict(message='authentication_required'), 401

        try:
            security.validate_token(
                req_args.token, current_app.config['SECRET_KEY'], max_age=300)
        except itsdangerous.SignatureExpired:
            return dict(message='token_expired'), 401
        except itsdangerous.BadData:
            return dict(message='invalid_token'), 401

        return func(*args, **kwargs)

    return decorator


def build_edit_post_parser():
    parser = reqparse.RequestParser()
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
        storage = current_app.extensions['pblog'].storage
        md = current_app.extensions['pblog'].markdown
        args = parser.parse_args()

        try:
            post_package = read_package(args.post.stream)
        except PackageValidationError as e:
            return dict(errors=e.errors), 400
        except PackageException as e:
            return dict(errors={'__all__': [str(e)]})

        post_package.set_default_values()
        post_package.build_html_content(md)
        post = storage.create_post(post_package)

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
        storage = current_app.extensions['pblog'].storage
        md = current_app.extensions['pblog'].markdown

        try:
            post = storage.get_post(post_id)
        except NoResultFound:
            return {'post': ["The post with id {} does not exist".format(post_id)]}, 404

        parser = build_edit_post_parser()
        args = parser.parse_args()

        try:
            post_package = read_package(args.post.stream)
        except PackageValidationError as e:
            return dict(errors=e.errors), 400
        except PackageException as e:
            return dict(errors={'__all__': [str(e)]})

        post_package.set_default_values()
        post_package.build_html_content(md)
        storage.update_post(post, post_package)

        post_schema = PostSchema()
        return post_schema.dump(post).data


@api.resource('/', '/<path:path>')
class NotFound(Resource):
    def dispatch_request(self, *args, **kwargs):
        return dict(message='not found'), 404
