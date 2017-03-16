from urllib.parse import urlparse


class TestShowPost:
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
