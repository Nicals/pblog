from contextlib import contextmanager
import pathlib
from unittest.mock import patch
from urllib.parse import urlparse

from flask import template_rendered


@contextmanager
def capture_template(app):
    recorded = []

    def record(sender, template, context, **kwargs):
        recorded.append((template, context))
    template_rendered.connect(record, app)

    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class TestPostsList:
    def test_renders_template(self, post, app, client):
        with capture_template(app) as templates:
            response = client.get('/')

            assert response.status_code == 200
            assert len(templates) >= 1
            assert templates[0][0].name == 'pblog/posts-list.html'


class TestShowPost:
    def test_template_rendered(self, post, app, client):
        with capture_template(app) as templates:
            response = client.get('/post/%d/%s' % (post.id, post.slug))

            assert response.status_code == 200
            assert len(templates) >= 1
            assert templates[0][0].name == 'pblog/post.html'

    def test_corrects_slug(self, post, client):
        response = client.get('/post/%d/invalid-slug' % post.id, follow_redirects=False)

        assert response.status_code == 301
        assert urlparse(response.location).path == '/post/%d/%s' % (post.id, post.slug)

    def test_corrects_slug_on_markdown(self, post, client):
        response = client.get('/post/%d/invalid-slug.md' % post.id, follow_redirects=False)

        assert response.status_code == 301
        assert urlparse(response.location).path == '/post/%d/%s.md' % (post.id, post.slug)

    def test_raises_404(self, client):
        response = client.get('/post/1/foo')

        assert response.status_code == 404

    def test_shows_html(self, post, client):
        response = client.get('/post/%d/%s' % (post.id, post.slug))

        assert response.status_code == 200
        assert response.headers['Content-Type'].startswith('text/html') is True

    def test_shows_markdown(self, post, client):
        response = client.get('/post/%d/%s.md' % (post.id, post.slug))

        assert response.status_code == 200
        assert response.headers['Content-Type'].startswith('text/plain') is True


class TestShowPostsInTopic:
    def test_template_rendered(self, post, app, client):
        with capture_template(app) as templates:
            response = client.get('/topic/%d/%s' % (post.topic.id,
                                                    post.topic.slug))

            assert response.status_code == 200
            assert len(templates) >= 1
            assert templates[0][0].name == 'pblog/posts-list.html'

    def test_corrects_slug(self, post, app, client):
        response = client.get('/topic/%d/invalid-slug' % post.topic.id,
                              follow_redirects=False)

        assert response.status_code == 301
        location = urlparse(response.location).path
        assert location == '/topic/%s/%s' % (post.topic.id, post.topic.slug)

    def test_raises_404(self, app, client):
        response = client.get('/topic/1/foo')

        assert response.status_code == 404


@patch('flask_pblog.views.send_from_directory', autospec=True)
def test_serves_resource_file(patch_send_from_directory, app, client):
    resource_path = pathlib.Path('/foo/bar/resources')
    client.application.extensions['pblog'].post_resource_path = resource_path
    patch_send_from_directory.return_value = b'file content'

    response = client.get('/resources/some-file.txt')

    assert response.status_code == 200
    assert response.data == b'file content'
    patch_send_from_directory.assert_called_once_with(resource_path, 'some-file.txt')


class TestShow404:
    def test_renders_template(self, app, client):
        with capture_template(app) as templates:
            response = client.get('/unexisting')

            assert response.status_code == 404
            assert len(templates) >= 1
            assert templates[0][0].name == 'pblog/404.html'
