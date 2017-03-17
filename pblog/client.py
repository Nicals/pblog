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
    def _init__(self, expected_status, received_status):
        super().__init__("Expecing %s response, but got %s" % (
            expected_status, received_status))


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
            'category': {'type': 'dict', 'schema': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
            }},
            'published_date': {
                'type': 'date',
                'coerce': lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date()},
        })

        if not validator.validate(post):
            raise Client(validator.errors)

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

    def create_post(self, post_path, encoding):
        """
        Args:
            post_file (pathlib.Path):
            encoding (str): encoding of the post file

        Returns:
            dict: The api response
        """
        response = self.session.post(
            '{}/posts'.format(self.api_root),
            data={
                'encoding': encoding,
            },
            files={
                'post': (post_path.name, post_path.open(), 'text/markdown'),
            })

        return self.normalize_post(self._read_response(response, [201]))

    def update_post(self, post_id, post_path, encoding):
        """
        Args:
            post_id (integer): id of the post to update
            post_path (pathlib.Path):
            encoding (str):

        Returns:
            dict: The api response
        """
        response = self.session.post(
            '{}/posts/{}'.format(self.api_root, post_id),
            data={
                'encoding': encoding,
            },
            files={
                'post': (post_path.name, post_path.open(), 'text/markdown'),
            })

        return self.normalize_post(self._read_response(response, [200]))
