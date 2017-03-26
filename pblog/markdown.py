from collections import namedtuple

from cerberus import DocumentError, Validator
from datetime import date
import markdown
from markdown_extra.meta import inject_meta
from slugify import slugify
import yaml


class PostError(Exception):
    """Raised when building a post is impossible
    """
    def __init__(self, message, errors):
        """
        Args:
            message (str): General message describing errors
            errors (dict): Dictionnary mappings field name to a list of string
                describing errors that occured.
        """
        self.errors = errors
        super().__init__(message)


validator = Validator({
    'id': {'type': 'dict',
           'default': {},
           'required': False,
           'keyschema': {'type': 'string'},
           'valueschema': {'type': 'integer', 'default': None, 'nullable': True}},
    'title': {'type': 'string',
              'required': True},
    'slug': {'type': 'string',
             'default': None,
             'nullable': True,
             'required': False,
             'regex': '^[A-Za-z0-9_-]+$'},
    'category': {'type': 'string',
                 'required': True},
    'date': {'type': 'date',
             'nullable': True,
             'default': None},
})


PostDefinition = namedtuple('PostDefinition', (
    'id', 'title', 'slug', 'summary', 'date', 'category', 'markdown', 'html'))


def update_meta(md_file, meta, encoding='utf-8'):
    """Replace some markdown file metadata by others.

    Args:
        md_file (file): The file to replace
        meta (dict):
        encoding (str):
    """
    new_content = inject_meta(md_file.read().decode(encoding), meta, update=True)
    md_file.seek(0)
    md_file.write(new_content.encode(encoding))


def parse_markdown(md_file, encoding='utf-8', md=None):
    """Extract and validates all post data from a markdown file.

    Args:
        md_file (file): The file to parse.
        encoding (str): The encoding used in the file.
        md (markdown.Markdown): Markdown instance to use to parse the post
            file. The markdown instance must have at lest the following
            extensions enabled: ``markdown_extra.meta`` ``markdown_extra.summary``
            If some of these extensions are missing, they will be automatically
            registered into the markdown instance.
            If none, a markdown instance with minimal extensions will be built.

    Returns:
        PostDefinition: The data extracted from the file

    Raises:
        PostError: If any data fails to correctly validate
    """
    required_exts = ['markdown_extra.summary', 'markdown_extra.meta']
    if md is None:
        md = markdown.Markdown(extensions=required_exts)
    else:
        # make sure we have the required extensions
        for ext in required_exts:
            if ext not in md.registeredExtensions:
                md.registerExtensions([ext], {})

    md.reset()

    try:
        md_content = md_file.read().decode(encoding)
    except UnicodeDecodeError:
        raise PostError(
            "Markdown file is not {} compatible".format(encoding),
            errors={'encoding': ["document could not be interpreted with {}".format(encoding)]})
    except LookupError:
        raise PostError(
            "Encoding {} is not valid".format(encoding),
            errors={'encoding': ["unknown encoding {}".format(encoding)]})

    try:
        html_content = md.convert(md_content)
    except yaml.YAMLError:
        raise PostError(
            "meta is not valid yaml",
            errors={'markdown': ["could not parse header"]})

    try:
        if not validator.validate(md.meta):
            raise PostError("Meta data did not validate", errors=validator.errors)
    except DocumentError:
        raise PostError("No meta", errors={'': 'No meta'})

    meta = validator.normalized(md.meta)

    if meta['slug'] is None:
        meta['slug'] = slugify(meta['title'])

    if meta['date'] is None:
        meta['date'] = date.today()

    return PostDefinition(
        summary=md.summary if md.summary is not None else '',
        markdown=md_content,
        html=html_content,
        **meta)
