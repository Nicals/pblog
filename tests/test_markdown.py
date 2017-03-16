from datetime import date
from io import BytesIO

import pytest

from pblog import markdown


def test_extracts_post_info():
    md_file = BytesIO("""---

title: A title
slug: a-title
category: A category
date: 2017-05-12

---

First paragraph

Second paragraph
    """.encode('utf-8'))

    post = markdown.parse_markdown(md_file)

    assert post.id == {}
    assert post.title == "A title"
    assert post.slug == "a-title"
    assert post.category == "A category"
    assert post.date == date(2017, 5, 12)


def test_raise_validation_error_if_no_meta_data():
    md_file = BytesIO("""---

---

first paragraph
""".encode('utf-8'))

    with pytest.raises(markdown.PostError):
        markdown.parse_markdown(md_file)


def test_updates_meta():
    md_file = BytesIO("""---

title: foo

---

Paragraph éà
""".encode('utf-8'))

    markdown.update_meta(md_file, {'id': 12})

    md_file.seek(0)
    file_content = md_file.read().decode('utf-8')

    assert 'title: foo' in file_content
    assert 'id: 12' in file_content


class TestValidator:
    def test_id_rules(self):
        markdown.validator.validate({'id': {'foo': 12, 'bar': None}})

        assert 'id' not in markdown.validator.errors

    def test_empty_id(self):
        markdown.validator.validate({})

        assert 'id' not in markdown.validator.errors

    def test_normalizes_id_to_dict(self):
        meta = markdown.validator.normalized({
            'title': 'Foo', 'slug': 'Foo', 'category': 'Cat'})

        assert meta['id'] == {}
