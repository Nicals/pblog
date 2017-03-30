from datetime import date
from io import BytesIO
import tarfile
from unittest.mock import patch
import yaml

import pytest

from pblog import package


SAMPLE_MARKDOWN = """---
title: This is a title
category: A category
---

[summary]
Let's have a summary

And at least a paragraph with special chars: éçà.
"""
SAMPLE_HTML = "<p>And at least a paragraph with special chars: éçà.</p>"


def add_tar_member(tar, name, content):
    content_file = BytesIO(content)
    file_info = tarfile.TarInfo(name)
    file_info.size = len(content)
    tar.addfile(file_info, content_file)


def build_tar_file(content_files):
    tar_file = BytesIO()
    with tarfile.open(mode='w', fileobj=tar_file) as tar:
        for name, content in content_files:
            add_tar_member(tar, name, content)
    tar_file.seek(0)
    return tar_file


def test_extracts_package_meta():
    pack = build_tar_file([
        ('package.yml', b"encoding: utf-8\npost: post.md\n")])

    with tarfile.open(fileobj=pack) as tar:
        assert package.extract_package_meta(tar) == {
            'encoding': 'utf-8',
            'post': 'post.md',
        }


def test_empty_package_meta_raise_error():
    pack = build_tar_file([('package.yml', b"")])

    with tarfile.open(fileobj=pack) as tar:
        with pytest.raises(package.PackageException):
            package.extract_package_meta(tar)


def test_wrong_yaml_package_meta_raise_error():
    pack = build_tar_file([('package.yml', b"'")])

    with tarfile.open(fileobj=pack) as tar:
        with pytest.raises(package.PackageException):
            package.extract_package_meta(tar)


def test_raise_exception_if_no_package_meta():
    pack = build_tar_file([('not-package.yml', b"some content'")])

    with tarfile.open(fileobj=pack) as tar:
        with pytest.raises(package.PackageException):
            package.extract_package_meta(tar)


def test_raise_exception_if_package_meta_do_not_validate():
    pack = build_tar_file([('package.yml', b"foo: bar\n")])

    with tarfile.open(fileobj=pack) as tar:
        with pytest.raises(package.PackageValidationError) as excinfo:
            package.extract_package_meta(tar)

    assert 'encoding' in excinfo.value.errors
    assert 'post' in excinfo.value.errors


def test_normalize_post_meta():
    meta = package.normalize_post_meta({'title': 'Title', 'category': 'Category'})

    assert meta == {
        'id': {},
        'title': 'Title',
        'slug': None,
        'category': 'Category',
        'published_date': None,
    }


def test_normalize_post_meta_validation():
    with pytest.raises(package.PackageValidationError) as excinfo:
        package.normalize_post_meta({})

    assert 'title' in excinfo.value.errors
    assert 'category' in excinfo.value.errors


def test_read_package(temp_dir):
    pack = build_tar_file([
        ('package.yml', b"encoding: iso-8859-1\npost: post.md"),
        ('post.md', SAMPLE_MARKDOWN.encode('iso-8859-1')),
    ])
    package_path = temp_dir / 'package.tar.gz'
    with package_path.open('wb') as f:
        f.write(pack.read())

    package_info = package.read_package(package_path)

    assert package_info.post_encoding == 'iso-8859-1'
    assert package_info.post_id == {}
    assert package_info.post_title == "This is a title"
    assert package_info.post_slug is None
    assert package_info.category_name == "A category"
    assert package_info.published_date is None
    assert package_info.summary == "Let's have a summary"
    assert package_info.markdown_content == SAMPLE_MARKDOWN
    assert package_info.html_content == SAMPLE_HTML


def test_read_package_from_file():
    package_file = build_tar_file([
        ('package.yml', b"encoding: iso-8859-1\npost: post.md"),
        ('post.md', SAMPLE_MARKDOWN.encode('iso-8859-1')),
    ])

    package_info = package.read_package(package_file)

    assert package_info.post_title == "This is a title"


def test_build_package(temp_dir):
    post_path = temp_dir / "post.md"
    package_file = BytesIO()
    with post_path.open('w', encoding='iso-8859-1') as post_file:
        post_file.write(SAMPLE_MARKDOWN)

    package.build_package(post_path, package_file, encoding='iso-8859-1')
    package_file.seek(0)

    with tarfile.open(mode='r', fileobj=package_file) as tar:
        meta_content = yaml.load(tar.extractfile('package.yml').read().decode())
        assert meta_content == {'encoding': 'iso-8859-1', 'post': 'post.md'}
        assert tar.extractfile('post.md').read().decode('iso-8859-1') == SAMPLE_MARKDOWN


def test_build_package_writes_on_disc(temp_dir):
    post_path = temp_dir / "post.md"
    with post_path.open('w', encoding='utf-8') as post_file:
        post_file.write(SAMPLE_MARKDOWN)
    package_path = temp_dir / "package.tar.gz"

    package.build_package(post_path, package_path)

    assert package_path.is_file()
    try:
        with tarfile.open(str(package_path)):
            pass
    except tarfile.ReadError:
        pytest.fail("built package is not a valid tar file")


def test_invalid_post_meta_will_not_package(temp_dir):
    post_path = temp_dir / "post.md"
    with post_path.open('w') as f:
        f.write("""---
foo: bar
""")

    with pytest.raises(package.PackageValidationError) as excinfo:
        package.build_package(post_path, BytesIO())

    assert 'title' in excinfo.value.errors
    assert 'category' in excinfo.value.errors


@patch('pblog.package.date')
def test_package_sets_default_values(patch_date):
    patch_date.today.return_value = date(2017, 3, 30)
    pack = package.Package("A title", "A category", "Some markdown", "summary")

    pack.set_default_values()

    assert pack.post_slug == 'a-title'
    assert patch_date.today.called
    assert pack.published_date == date(2017, 3, 30)
