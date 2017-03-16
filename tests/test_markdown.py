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

    assert post.id is None
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
