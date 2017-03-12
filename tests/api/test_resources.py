from unittest.mock import patch, Mock

import itsdangerous

from pblog.api import resources


@patch('pblog.api.resources.reqparse.RequestParser')
class TestAuthRequired:
    @patch('pblog.api.resources.security')
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

    @patch('pblog.api.resources.security')
    def test_expired_signature(self, security_patch, RequestParser, app):
        security_patch.validate_token.side_effect = itsdangerous.SignatureExpired('expired')
        view = Mock()

        response, status_code = resources.auth_required(view)()

        assert view.called is False
        assert status_code == 401
        assert response == {'message': 'token_expired'}

    def test_no_signature(self, RequestParser, app):
        view = Mock()

        response, status_code = resources.auth_required(view)()

        assert view.called is False
        assert status_code == 401
        assert response == {'message': 'invalid_token'}
