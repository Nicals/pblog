import datetime

from pblog import client


def test_normalizes_post():
    cl = client.Client('/')

    post = cl.normalize_post({
        'slug': 'a-slug',
        'title': 'A title',
        'published_date': '2017-03-16',
        'topic': {'name': 'Programming', 'id': 1},
        'id': 1})

    assert post == {
        'id': 1,
        'title': 'A title',
        'slug': 'a-slug',
        'published_date': datetime.date(2017, 3, 16),
        'topic': {'name': 'Programming', 'id': 1}}
