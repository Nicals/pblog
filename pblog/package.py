"""This module handles post package operations

A package is a compressed tarfile which contains all post informations,
including generatl metadata and markdown post file.

The package must contains a ``package.yml`` file at his root.
This file provides general metadata about file structure:

.. code:: yaml

   # encoding used in the markdown file
   encoding: utf-8
   # path of the markdown file in the package
   post: post.md
"""

from io import IOBase, BytesIO
from datetime import date
import pathlib
import tarfile
import yaml

import cerberus
from markdown import Markdown
from slugify import slugify


__all__ = [
    'PackageException',
    'PackageValidationError',
    'read_package',
    'build_package',
    'Package',
]


class PackageException(Exception):
    """Base exception for post packaging"""


class PackageValidationError(PackageException):
    """A package was found not valid.

    Attributes:
        errors (dict): A dictionary mapping field names to a list of error
            string.
    """
    def __init__(self, message, errors):
        """
        Args:
            message (str): generic error description
            errors (dict): detailed errors
        """
        super().__init__(message)
        self.errors = errors


def build_markdown_parser(parser=None):
    """Builds or add required extensions to a markdow parser
    instance to process posts.

    Args:
        parser (markdow.Markdown): If given, all required extensions for
            post packaging will be added to this parser instance.

    Returns:
        markdown.Markdown: A ready to use markdown parser instance.
    """
    required_extensions = [
        'markdown_extra.summary',
        'markdown_extra.meta',
    ]

    if parser is None:
        parser = Markdown()

    for extension_name in required_extensions:
        if extension_name not in parser.registeredExtensions:
            parser.registerExtensions([extension_name], {})

    parser.reset()

    return parser


def extract_package_meta(tar):
    """Reads and validate package metadata from tarfile.

    Args:
        tarfile.TarFile: opened package object

    Raises:
        pblog.package.PackageException: If the package.yml file is not
            present in the post package archive.
        pblog.package.PackageValidationError: If the metadata fails to validate.
        UnicodeDecodeError: If the package encoding is not utf-8

    Returns:
        dict: extracted metadata
    """
    validator = cerberus.Validator({
        'post': {
            'type': 'string',
            'required': True,
        },
        'encoding': {
            'type': 'string',
            'required': True,
        },
    })
    try:
        meta = yaml.load(tar.extractfile('package.yml').read().decode())
    except yaml.YAMLError:
        raise PackageException(
            "The package.yml file does not contain valid YAML")
    except KeyError:
        raise PackageException(
            "The package does not contains a package.yml file")
    if meta is None:
        raise PackageException("package.yml file is empty")
    if not validator.validate(meta):
        raise PackageValidationError(
            "Package metadata is not valid", validator.errors)
    return meta


def normalize_post_meta(post_meta):
    """Check that some post metadata are valid.

    Raises:
        pblog.package.PackageValidationError: If the metadata are not valid
    """
    validator = cerberus.Validator({
        'id': {
            'type': 'dict',
            'required': False,
            'default': {},
            'keyschema': {'type': 'string'},
            'valueschema': {'type': 'integer', 'default': None, 'nullable': True},
        },
        'title': {
            'type': 'string',
            'required': True,
        },
        'slug': {
            'type': 'string',
            'nullable': True,
            'required': False,
            'default': None,
            'regex': '^[A-Za-z0-9_-]+$',
        },
        'category': {
            'type': 'string',
            'required': True,
        },
        'published_date': {
            'type': 'date',
            'nullable': True,
            'default': None,
        },
    })

    if not validator.validate(post_meta):
        raise PackageValidationError(
            "Post metadata did not validate", validator.errors)

    return validator.normalized(post_meta)


def read_package(package_path, parser=None):
    """
    Args:
        package_path (pathlib.Path or file oject): path to the package file
            to read
        parser (markdown.Markdown): a markdown parser instance. If not
            given, a minimalistic parser will be used.

    Returns:
        pblog.package.Package: An instance containing extracted post data.
    """
    tar_kwargs = dict(mode='r')
    if isinstance(package_path, pathlib.Path):
        tar_kwargs['name'] = str(package_path)
    elif isinstance(package_path, IOBase):
        tar_kwargs['fileobj'] = package_path
    else:
        raise ValueError(
            "package_path should be pathlib.Path or file-object instance. "
            "%s instead" % type(package_path))

    parser = build_markdown_parser(parser)
    with tarfile.open(**tar_kwargs) as tar:
        package_meta = extract_package_meta(tar)
        post_member = package_meta['post']
        post_encoding = package_meta['encoding']

        post_md_content = tar.extractfile(post_member).read().decode(post_encoding)
        post_html_content = parser.convert(post_md_content)
        post_meta = normalize_post_meta(parser.meta)

        package_info = Package(
            post_encoding=post_encoding,
            post_id=post_meta['id'],
            post_title=post_meta['title'],
            post_slug=post_meta['slug'],
            category_name=post_meta['category'],
            published_date=post_meta['published_date'],
            summary=parser.summary,
            markdown_content=post_md_content,
            html_content=post_html_content,
        )

        return package_info


def build_package(post_path, package_path, encoding='utf-8'):
    """Build a package for a post.

    Args:
        post_path (pathlib.Path): path to the markdown post
        package_path (pathlib.Path or file object): path to the package to
            create, or file-like object to write the package into.
        encoding (str): encoding of the markdown post file
    """
    parser = build_markdown_parser()
    with post_path.open(encoding=encoding) as post_file:
        parser.convert(post_file.read())

    normalize_post_meta(parser.meta)
    package_meta = yaml.dump(dict(post=post_path.name, encoding=encoding)).encode()

    tar_kwargs = dict(mode='w')
    if isinstance(package_path, pathlib.Path):
        tar_kwargs['name'] = str(package_path)
    elif isinstance(package_path, IOBase):
        tar_kwargs['fileobj'] = package_path
    else:
        raise ValueError(
            "package_path should be a pathlib.Path or file-object instance. "
            "%s instead" % type(package_path))

    with tarfile.open(**tar_kwargs) as tar:
        # write package metadata
        content = BytesIO(package_meta)
        file_info = tarfile.TarInfo('package.yml')
        file_info.size = len(package_meta)
        tar.addfile(file_info, content)

        # write post
        tar.add(str(post_path), arcname=post_path.name)


class Package:
    """Holds package information.

    Attributes:
        file_encoding (string): encoding of the markdown post
        post_id (dict):
        post_title (string):
        post_slug (string):
        category_name (string):
        published_date (date):
        summary (string):
        markdown_content (string):
        html_content (string):
    """
    def __init__(self, post_title, category_name, markdown_content,
                 summary, post_encoding='utf-8', post_id=None, post_slug=None,
                 published_date=None, html_content=None):
        self.post_encoding = post_encoding
        self.post_id = post_id
        self.post_title = post_title
        self.post_slug = post_slug
        self.category_name = category_name
        self.published_date = published_date
        self.summary = summary
        self.markdown_content = markdown_content
        self.html_content = html_content

    def set_default_values(self):
        """Sets missing values in the post.

        If ``post_slug`` is None, it will be generated from ``post_title``.
        If ``published_date`` is None, it will be set to the current date.
        """
        if self.post_slug is None:
            self.post_slug = slugify(self.post_title)

        if self.published_date is None:
            self.published_date = date.today()
