from contextlib import contextmanager
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
    def test_template_renderd(self, post, app, client):
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

    def test_raises_404(self, client, db):
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


class TestShow404:
    def test_renders_template(self, db, app, client):
        with capture_template(app) as templates:
            response = client.get('/unexisting')

            assert response.status_code == 404
            assert len(templates) >= 1
            assert templates[0][0].name == 'pblog/404.html'
