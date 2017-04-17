from datetime import date
from io import BytesIO
import pathlib
import tarfile
from unittest.mock import patch
import yaml

import pytest

from pblog import package


SAMPLE_MARKDOWN = """---
title: This is a title
topic: A topic
---

[summary]
Let's have a summary

And at least a paragraph with special chars: éçà.
"""
SAMPLE_HTML = "<p>And at least a paragraph with special chars: éçà.</p>"
PNG_HEADER = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'


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


def test_normalize_path():
    assert package.normalize_path(pathlib.Path('/foo/../bar')) == pathlib.Path('/bar')


class TestExtractPackageMeta:
    def test_extracts_package_meta(self):
        pack = build_tar_file([
            ('package.yml', b"encoding: utf-8\npost: post.md\n")])

        with tarfile.open(fileobj=pack) as tar:
            assert package.extract_package_meta(tar) == {
                'encoding': 'utf-8',
                'post': 'post.md',
            }

    def test_empty_package_meta_raise_error(self):
        pack = build_tar_file([('package.yml', b"")])

        with tarfile.open(fileobj=pack) as tar:
            with pytest.raises(package.PackageException):
                package.extract_package_meta(tar)

    def test_wrong_yaml_package_meta_raise_error(self):
        pack = build_tar_file([('package.yml', b"'")])

        with tarfile.open(fileobj=pack) as tar:
            with pytest.raises(package.PackageException):
                package.extract_package_meta(tar)

    def test_raise_exception_if_no_package_meta(self):
        pack = build_tar_file([('not-package.yml', b"some content'")])

        with tarfile.open(fileobj=pack) as tar:
            with pytest.raises(package.PackageException):
                package.extract_package_meta(tar)

    def test_raise_exception_if_package_meta_do_not_validate(self):
        pack = build_tar_file([('package.yml', b"foo: bar\n")])

        with tarfile.open(fileobj=pack) as tar:
            with pytest.raises(package.PackageValidationError) as excinfo:
                package.extract_package_meta(tar)

        assert 'encoding' in excinfo.value.errors
        assert 'post' in excinfo.value.errors


class TestPostMetaNormalization:
    def test_normalizes(self):
        meta = package.normalize_post_meta({'title': 'Title', 'topic': 'Category'})

        assert meta == {
            'id': {},
            'title': 'Title',
            'slug': None,
            'topic': 'Category',
            'published_date': None,
        }

    def test_validation(self):
        with pytest.raises(package.PackageValidationError) as excinfo:
            package.normalize_post_meta({})

        assert 'title' in excinfo.value.errors
        assert 'topic' in excinfo.value.errors


class TestExtractPackageResource:
    def test_resources_must_exist(self):
        pack = build_tar_file([
            ('resources/ham.png', PNG_HEADER),
            ('resources/spam/egg.png', PNG_HEADER)
        ])

        with tarfile.open(fileobj=pack) as tar:
            with pytest.raises(package.ResourcesNotFound) as excinfo:
                package.extract_package_resources(
                    tar, (pathlib.Path('ham.png'),
                          pathlib.Path('spam.png'),
                          pathlib.Path('spam/')))

        assert excinfo.value.resources == ['spam.png', 'spam']

    def test_resource_are_extracted(self):
        pack = build_tar_file([
            ('resources/imgs/ham.png', PNG_HEADER),
        ])

        with tarfile.open(fileobj=pack) as tar:
            resources = package.extract_package_resources(
                tar, (pathlib.Path('imgs/ham.png'),))

        assert len(resources) == 1
        resource = resources[0]
        assert resource.content == PNG_HEADER
        assert resource.path == pathlib.Path('imgs/ham.png')


class TestReadingPackage:
    def test_read_package(self, temp_dir):
        sample_markdown = SAMPLE_MARKDOWN + "![img](img.png)"
        pack = build_tar_file([
            ('package.yml', b"encoding: iso-8859-1\npost: post.md"),
            ('post.md', sample_markdown.encode('iso-8859-1')),
            ('resources/img.png', PNG_HEADER),
        ])
        package_path = temp_dir / 'package.tar.gz'
        with package_path.open('wb') as f:
            f.write(pack.read())

        package_info = package.read_package(package_path)

        assert package_info.post_encoding == 'iso-8859-1'
        assert package_info.post_id == {}
        assert package_info.post_title == "This is a title"
        assert package_info.post_slug is None
        assert package_info.topic_name == "A topic"
        assert package_info.published_date is None
        assert package_info.summary == "Let's have a summary"
        assert package_info.markdown_content == sample_markdown
        assert len(package_info.resources) == 1
        assert package_info.resources[0].path == pathlib.Path('img.png')
        assert package_info.resources[0].content == PNG_HEADER

    def test_read_package_from_file(self):
        package_file = build_tar_file([
            ('package.yml', b"encoding: iso-8859-1\npost: post.md"),
            ('post.md', SAMPLE_MARKDOWN.encode('iso-8859-1')),
        ])

        package_info = package.read_package(package_file)

        assert package_info.post_title == "This is a title"


class TestBuildingPackage:
    def test_build_package(self, temp_dir):
        post_path = temp_dir / "post.md"
        package_file = BytesIO()
        sample_markdown = SAMPLE_MARKDOWN + "![img](imgs/img.png)"
        with post_path.open('w', encoding='iso-8859-1') as post_file:
            post_file.write(sample_markdown)
        (temp_dir / 'imgs').mkdir()
        with (temp_dir / 'imgs/img.png').open('wb') as f:
            f.write(b'img-content')

        built_package = package.build_package(post_path, package_file, encoding='iso-8859-1')
        package_file.seek(0)

        with tarfile.open(mode='r', fileobj=package_file) as tar:
            meta_content = yaml.load(tar.extractfile('package.yml').read().decode())
            assert meta_content == {'encoding': 'iso-8859-1', 'post': 'post.md'}
            assert tar.extractfile('post.md').read().decode('iso-8859-1') == sample_markdown
            assert tar.extractfile('resources/imgs/img.png').read() == b'img-content'

        assert built_package.post_id == {}
        assert built_package.post_title == "This is a title"
        assert built_package.post_slug is None
        assert built_package.published_date is None
        assert built_package.topic_name == "A topic"
        assert built_package.markdown_content == sample_markdown
        assert len(built_package.resources) == 1
        resource = built_package.resources[0]
        assert resource.content == b'img-content'
        assert resource.path == pathlib.Path('imgs/img.png')

    def test_build_package_writes_on_disc(self, temp_dir):
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

    def test_invalid_post_meta_will_not_package(self, temp_dir):
        post_path = temp_dir / "post.md"
        with post_path.open('w') as f:
            f.write("""---
foo: bar
""")

        with pytest.raises(package.PackageValidationError) as excinfo:
            package.build_package(post_path, BytesIO())

        assert 'title' in excinfo.value.errors
        assert 'topic' in excinfo.value.errors

    def test_ensures_resource_file_are_found(self, temp_dir):
        with (temp_dir / 'image.png').open('w') as f:
            f.write('some random content')
        with (temp_dir / 'post.md').open('w') as f:
            f.write(SAMPLE_MARKDOWN + """
![unexisting-image](unexisting.png)
![existing-image](image.png)
""")

        with pytest.raises(package.ResourcesNotFound) as excinfo:
            package.build_package(temp_dir / 'post.md', temp_dir / 'post.tar.gz')

        assert excinfo.value.resources == ['unexisting.png']


class TestPackage:
    @patch('pblog.package.date')
    def test_package_sets_default_values(self, patch_date):
        patch_date.today.return_value = date(2017, 3, 30)
        pack = package.Package("A title", "A topic", "Some markdown", "summary")

        pack.set_default_values()

        assert pack.post_slug == 'a-title'
        assert patch_date.today.called
        assert pack.published_date == date(2017, 3, 30)

    def test_package_update_post_meta(self):
        pack = package.Package(
            post_title="A title", topic_name="A topic",
            markdown_content=SAMPLE_MARKDOWN, summary="Foo")

        assert pack.update_post_meta(
            post_slug='a-title',
            published_date=date(2017, 3, 30),
            post_id={'foo': 12}) is True
        assert pack.post_slug == 'a-title'
        assert pack.published_date == date(2017, 3, 30)
        assert pack.post_id == {'foo': 12}

        parser = package.markdown_parser
        package.markdown_parser.convert(pack.markdown_content)
        assert parser.meta['slug'] == 'a-title'
        assert parser.meta['published_date'] == date(2017, 3, 30)
        assert parser.meta['id'] == {'foo': 12}

    def test_package_warns_if_no_meta_to_update(self):
        pack = package.Package(
            post_title="A title", topic_name="A topic",
            markdown_content="", post_slug="slug", summary="Foo",
            published_date=date(2017, 3, 30), post_id={'foo': 12})

        assert pack.update_post_meta(
            post_id={'foo': 12},
            post_slug='slug', published_date=date(2017, 3, 30)) is False


class TestResourceHandler:
    def test_only_accepts_relative_path(self):
        with pytest.raises(ValueError):
            package.ResourceHandler(b'', pathlib.Path('/foo/bar'))

    def test_ensures_root_path_exists(self, temp_dir):
        res_hdl = package.ResourceHandler(b'', pathlib.Path('blah'))

        with pytest.raises(FileNotFoundError):
            res_hdl.save(temp_dir / 'not-existing')

    def test_ensure_no_root_path_escape(self, temp_dir):
        (temp_dir / 'ham').mkdir()
        res_hdl = package.ResourceHandler(PNG_HEADER, pathlib.Path('../spam'))

        with pytest.raises(package.PackageException):
            res_hdl.save(temp_dir / 'ham')

    def test_ensure_root_path_is_dir(self, temp_dir):
        with (temp_dir / 'foo').open('wb') as f:
            f.write(b'foo')
        res_hdl = package.ResourceHandler(b'', pathlib.Path('foo'))

        with pytest.raises(NotADirectoryError):
            res_hdl.save(temp_dir / 'foo')

    def test_writes_content(self, temp_dir):
        content = b'some content'
        res_path = pathlib.Path('foo/bar/content.dat')
        res_hdl = package.ResourceHandler(content, res_path)

        res_hdl.save(temp_dir)

        abs_res_path = temp_dir / res_path

        assert abs_res_path.exists(), "{} was not written".format(abs_res_path)
        assert abs_res_path.is_file()
        with abs_res_path.open('rb') as f:
            assert f.read() == content

    def test_creates_sub_directory(self, temp_dir):
        res_hdl = package.ResourceHandler(PNG_HEADER, pathlib.Path('img.png'))

        res_hdl.save(temp_dir, 'res')

        assert (temp_dir / 'res').exists()
        assert (temp_dir / 'res').is_dir()
        with (temp_dir / 'res/img.png').open('rb') as f:
            assert f.read() == PNG_HEADER
