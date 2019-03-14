import datetime

from cerberus import Validator
import requests


AUTH_HEADER = 'X-Pblog-Token'


class ClientException(Exception):
    pass


class AuthenticationError(ClientException):
    def __init__(self, code):
        super().__init__("401 response (%s)" % code)


class UnexpectedResponse(ClientException):
    def __init__(self, expected_status, received_status):
        self.expected_status = expected_status
        self.received_status = received_status
        super().__init__("Expecing %s response, but got %s" % (
            expected_status, received_status))


class ResponseContentError(ClientException):
    """Raised when the content of the response do not have the expected
    format"""
    def __init__(self, message, errors=None, content=None):
        """
        Args:
            message (str): general description of the error
            errors (dict): validation errors
        """
        super().__init__(message)
        self.errors = errors


class Client:
    """This client class is used to access the Pblog API.
    """
    def __init__(self, api_root):
        self.api_root = api_root.rstrip('/')

        self.session = requests.Session()

    def _read_response(self, response, expected_status=[200]):
        if 401 not in expected_status and response.status_code == 401:
            raise AuthenticationError(response.json()['message'])
        elif response.status_code not in expected_status:
            raise UnexpectedResponse(expected_status, response.status_code)

        return response.json()

    def normalize_post(self, post):
        """Normalizes a post response.

        Returns:
            dict: A normalized dictionary.
        """
        validator = Validator({
            'id': {'type': 'integer'},
            'title': {'type': 'string'},
            'slug': {'type': 'string'},
            'topic': {'type': 'dict', 'schema': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
            }},
            'published_date': {
                'type': 'date',
                'coerce': lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date()},
        })

        if not validator.validate(post):
            raise ResponseContentError(
                "Response from server did not validate %s" % post,
                errors=validator.errors)

        return validator.normalized(post)

    def authenticate(self, username, password):
        """Authenticate on the web api.

        Raises:
            pblog.client.AuthenticationError: if the authentication failed
        """
        response = self.session.post(
            '{}/auth'.format(self.api_root),
            data=dict(
                username=username,
                password=password))

        content = self._read_response(response, [200])
        self.session.headers[AUTH_HEADER] = content['token']

    def create_post(self, package_path):
        """
        Args:
            package_path (pathlib.Path): path to the package to send

        Returns:
            dict: The api response
        """
        response = self.session.post(
            '{}/posts'.format(self.api_root),
            files={
                'post': (package_path.name, package_path.open('rb'), 'application/tar+gzip'),
            })

        return self.normalize_post(self._read_response(response, [201]))

    def update_post(self, post_id, package_path):
        """
        Args:
            post_id (integer): id of the post to update
            package_path(pathlib.Path):
            encoding (str):

        Returns:
            dict: The api response
        """
        response = self.session.post(
            '{}/posts/{}'.format(self.api_root, post_id),
            files={
                'post': (package_path.name, package_path.open('rb'), 'application/tar+gzip'),
            })

        return self.normalize_post(self._read_response(response, [200]))
