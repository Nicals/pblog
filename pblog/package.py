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

If some resources (images, archive file, ...) are shipped with the post, they
will be stored in a "resources" directory at the root of the package path.
Those resources must be references from within the markdown file in order to
be extracted.
Otherwise, they are simply ignored.
"""

from io import IOBase, BytesIO
from datetime import date
import os
import pathlib
import tarfile
import yaml

import cerberus
from markdown import Markdown
from markdown_extra.meta import MetaExtension, inject_meta
from markdown_extra.summary import SummaryExtension
from markdown_extra.resource_path import ResourcePathExtension
from slugify import slugify


__all__ = [
    'PackageException',
    'PackageValidationError',
    'ResourcesNotFound',
    'ResourceHandler',
    'read_package',
    'build_package',
    'Package',
]


def normalize_path(path):
    """Ensure that an absolute path is the direct one to a file
    (no .. or other thinks).

    Args:
        path (pathlib.Path): the path to normalize

    Raises:
        ValueError: if the given path is not absolute

    Returns:
        pathlib.Path: normalized path
    """
    if not path.is_absolute():
        raise ValueError('path {} is not absolute'.format(path))

    return pathlib.Path(os.path.abspath(str(path)))


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


markdown_parser = Markdown(
    extensions=[
        MetaExtension(),
        SummaryExtension(),
        ResourcePathExtension(),
    ],
)


class ResourcesNotFound(PackageException):
    """This exception is raised whenever some resources files within a
    package are not existing.

    Attributes:
        resources (list): list of resources that weren't found
    """
    def __init__(self, resources):
        super().__init__("Some resources could not be found: {}".format(
            ', '.join(resources)))
        self.resources = resources


class ResourceHandler:
    """Wrapper around external post resource for easy filesystem manipulation.
    """
    def __init__(self, content, path):
        """
        Args:
            content (bytes): content of the resource file
            path (pathlib.Path): relative path of the resource

        Raises:
            ValueError: if the resource path is not a relative path
        """
        self.content = content
        if path.is_absolute():
            raise ValueError("path {} must be relative".format(path))
        self.path = path

    def save(self, root_path):
        """Write the resource in a given directory.

        Args:
            root_path (pathlib.Path): Where to save this resource

        Raises:
            FileNotFoundError: if the root_path does not exist
            NotADirectoryError: if the root_path is not a directory
            PackageException: if writing the file will get outside of
                root_directory.
        """
        root_path.resolve()
        if not root_path.is_dir():
            raise NotADirectoryError(
                "Root resource path {} is not a directory".format(root_path))

        resource_path = normalize_path(root_path / self.path)

        if root_path not in resource_path.parents:
            raise PackageException(
                "resource path {} is not within given root directory {}".format(
                    resource_path, root_path))

        try:
            resource_path.parent.mkdir(mode=0o755, parents=True)
        except FileExistsError:
            pass

        with resource_path.open('wb') as f:
            f.write(self.content)


def extract_package_meta(tar):
    """Reads and validate package metadata from tarfile.

    Args:
        tar (tarfile.TarFile): opened package object

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


def extract_package_resources(tar, resource_paths):
    """Extract given resources from a package

    Args:
        tar (tarfile.TarFile): the package
        resource_paths (list of pathlib.Path): path of resources to extract

    Raises:
        pblog.package.ResourcesNotFound: if some resources did not exist
            in the package

    Returns:
        list of pblog.package.ResourceHandler:
    """
    resources = []
    not_found = []

    for path in resource_paths:
        try:
            res_content = tar.extractfile(str('resources/' / path))
        except KeyError:
            not_found.append(str(path))

        resources.append(ResourceHandler(res_content.read(), path))

    if not_found:
        raise ResourcesNotFound(not_found)

    return resources


def read_package(package_path):
    """
    Args:
        package_path (pathlib.Path or file oject): path to the package file
            to read
        parser (markdown.Markdown): a markdown parser instance. If not
            given, a minimalistic parser will be used.

    Raises:
        UnicodeDecodeError: if the encoding of some file is not valid
        pblog.package.PackageValidationError: is the format of the package
            is not valid
        pblog.package.ResourcesNotFound: is some markdown resources could
            not be found in the package
        pblog.package.PackageException: if any other error occured

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

    with tarfile.open(**tar_kwargs) as tar:
        package_meta = extract_package_meta(tar)
        post_member = package_meta['post']
        post_encoding = package_meta['encoding']

        post_md_content = tar.extractfile(post_member).read().decode(post_encoding)
        markdown_parser.convert(post_md_content)
        post_meta = normalize_post_meta(markdown_parser.meta)
        resources = extract_package_resources(
            tar,
            (pathlib.Path(e[0]) for e in markdown_parser.resource_path))

        package_info = Package(
            post_encoding=post_encoding,
            post_id=post_meta['id'],
            post_title=post_meta['title'],
            post_slug=post_meta['slug'],
            category_name=post_meta['category'],
            published_date=post_meta['published_date'],
            summary=markdown_parser.summary,
            markdown_content=post_md_content,
            resources=resources,
        )

        return package_info


def get_resources(root_path, res_list):
    not_found = []
    resources = []

    for res_path, _ in res_list:
        try:
            abs_res_path = (root_path / res_path).resolve()
        except FileNotFoundError:
            not_found.append(res_path)
            continue

        if not abs_res_path.is_file():
            not_found.append(res_path)

        resources.append((abs_res_path, pathlib.Path(res_path)))

    if not_found:
        raise ResourcesNotFound(not_found)

    return resources


def build_package(post_path, package_path, encoding='utf-8'):
    """Build a package for a post.

    Args:
        post_path (pathlib.Path): path to the markdown post
        package_path (pathlib.Path or file object): path to the package to
            create, or file-like object to write the package into.
        encoding (str): encoding of the markdown post file

    Returns:
        package.Package: Information about the generated package
    """
    with post_path.open(encoding=encoding) as post_file:
        markdown_content = post_file.read()
    markdown_parser.convert(markdown_content)

    post_meta = normalize_post_meta(markdown_parser.meta)
    package_meta = yaml.dump(dict(post=post_path.name, encoding=encoding)).encode()
    resources = get_resources(post_path.parent, markdown_parser.resource_path)
    package_resources = []

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

        # write resources
        for abs_res_path, res_path in resources:
            tar.add(str(abs_res_path), str('resources' / res_path))
            with abs_res_path.open('rb') as res_file:
                package_resources.append(
                    ResourceHandler(res_file.read(), res_path))

    return Package(
        post_title=post_meta['title'],
        category_name=post_meta['category'],
        markdown_content=markdown_content,
        summary=markdown_parser.summary,
        post_encoding=encoding,
        post_id=post_meta['id'],
        post_slug=post_meta['slug'],
        published_date=post_meta['published_date'],
        resources=package_resources,
    )


class Package:
    """Holds package information.

    Attributes:
        post_title (string):
        category_name (string):
        markdown_content (string):
        summary (string):
        post_encoding (string): encoding of the markdown post
        post_id (dict):
        post_slug (string):
        published_date (date):
        html_content (string):
        resources (list): list of ResourceHandler instance
    """
    def __init__(self, post_title, category_name, markdown_content,
                 summary, post_encoding='utf-8', post_id={}, post_slug=None,
                 published_date=None, resources=[]):
        self.post_encoding = post_encoding
        self.post_id = post_id
        self.post_title = post_title
        self.post_slug = post_slug
        self.category_name = category_name
        self.published_date = published_date
        self.summary = summary
        self.markdown_content = markdown_content
        self.resources = resources
        self._html_content = None

    def build_html_content(self, parser):
        """Build internal HTML content from markdown content

        Args:
            parser markdown(Markdown): The parser to use for markdown
                conversion.
        """
        self._html_content = parser.convert(self.markdown_content)

    @property
    def html_content(self):
        if self._html_content is None:
            raise PackageException("html_content has not been generated")

        return self._html_content

    def set_default_values(self):
        """Sets missing values in the post.

        If ``post_slug`` is None, it will be generated from ``post_title``.
        If ``published_date`` is None, it will be set to the current date.
        """
        if self.post_slug is None:
            self.post_slug = slugify(self.post_title)

        if self.published_date is None:
            self.published_date = date.today()

    def update_post_meta(self, post_id, post_slug, published_date):
        """Update this instance attribute and reflect them in the markdown
        metadata.

        Args:
            post_id (dict): a new id to insert in the existing id collection
            post_slug (str):
            published_date (date):

        Returns:
            bool: True if some attribute needed to be updated and the
                markdown file was updated. False otherwise
        """
        need_update = False

        for env_name, env_id in post_id.items():
            if env_name in self.post_id:
                if self.post_id[env_name] != env_id:
                    need_update = True
                    continue
            else:
                need_update = True
                continue

        if post_slug != self.post_slug:
            need_update = True

        if published_date != self.published_date:
            need_update = True

        if not need_update:
            return False

        self.post_id.update(post_id)
        self.post_slug = post_slug
        self.published_date = published_date

        self.markdown_content = inject_meta(
            self.markdown_content,
            {
                'id': self.post_id,
                'slug': self.post_slug,
                'published_date': self.published_date,
            },
            update=True)

        return True
