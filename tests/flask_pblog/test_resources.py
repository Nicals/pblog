import json
from unittest.mock import patch, Mock

import itsdangerous

from flask_pblog import resources


@patch('flask_pblog.resources.reqparse.RequestParser')
class TestAuthRequired:
    @patch('flask_pblog.resources.security')
    def test_correct_key_allows_resource_access(self, security_patch, RequestParser, app):
        security_patch.validate_token.return_value = True
        view = Mock()

        resources.auth_required(view)()

        assert view.called is True
        assert security_patch.validate_token.called is True

    def test_wrong_signature_format(self, RequestParser, app):
        parser = Mock()
        parser.parse_args.return_value = Mock(token='foo')
        RequestParser.return_value = parser
        view = Mock()

        response, status_code = resources.auth_required(view)()

        assert status_code == 401
        assert response == {'message': 'invalid_token'}

    @patch('flask_pblog.resources.security')
    def test_expired_signature(self, security_patch, RequestParser, app):
        security_patch.validate_token.side_effect = itsdangerous.SignatureExpired('expired')
        view = Mock()

        response, status_code = resources.auth_required(view)()

        assert view.called is False
        assert status_code == 401
        assert response == {'message': 'token_expired'}

    def test_no_signature(self, RequestParser, app):
        parser = Mock(token=None)
        parser.parse_args.return_value = Mock(token=None)
        RequestParser.return_value = parser
        view = Mock()

        response, status_code = resources.auth_required(view)()

        assert view.called is False
        assert status_code == 401
        assert response == {'message': 'authentication_required'}


class TestPostListResource:
    @patch('flask_pblog.security.validate_token')
    def test_creates_new_post(self, validate_token, client, storage, post_package):
        response = client.post(
            '/api/posts',
            headers={'X-Pblog-Token': 'ham'},
            data={
                'post': (post_package, 'post.tar.gz'),
            })

        assert response.status_code == 201
        json_response = json.loads(response.data.decode())
        assert storage.get_post(json_response['id']).title == 'A title'


class TestPostResource:
    @patch('flask_pblog.security.validate_token')
    def test_updates_post(self, validate_token, client, storage, post, post_package):
        response = client.post(
            '/api/posts/%d' % post.id,
            headers={'X-Pblog-Token': 'ham'},
            data={
                'post': (post_package, 'post.md'),
            })

        assert response.status_code == 200
        json_response = json.loads(response.data.decode())
        assert json_response['id'] == post.id
        assert storage.get_post(post.id).title == 'A title'
