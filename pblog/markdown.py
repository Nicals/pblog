from collections import namedtuple

from cerberus import DocumentError, Validator
from datetime import date
import markdown
from markdown_extra.meta import inject_meta
import yaml


class PostError(Exception):
    """Raised when building a post is impossible

    Attributes:
        errors (dict): A dictionary mapping field name to a list of errors.
    """
    def __init__(self, message, errors):
        self.errors = errors
        super().__init__(message)


validator = Validator({
    'id': {'type': 'dict',
           'default': {},
           'nullable': True,
           'required': False,
           'keyschema': {'type': 'string'},
           'valueschema': {'type': 'integer', 'default': None, 'nullable': True}},
    'title': {'type': 'string', 'required': True},
    'slug': {'type': 'string', 'required': True, 'regex': '^[A-Za-z0-9_-]+$'},
    'category': {'type': 'string', 'required': True},
    'date': {'type': 'date'},
})


PostDefinition = namedtuple('PostDefinition', (
    'id', 'title', 'slug', 'summary', 'date', 'category', 'markdown', 'html'))


def update_meta(md_file, meta, encoding='utf-8'):
    """
    Args:
        md_file (file): The file to replace
        meta (dict):
        encoding (str):
    """
    new_content = inject_meta(md_file.read().decode(encoding), meta, update=True)
    md_file.seek(0)
    md_file.write(new_content.encode(encoding))


def parse_markdown(md_file, encoding='utf-8'):
    """Extract and validates all post data from a markdown file.

    Args:
        md_file (file): The file to parse.
        encoding (str): The encoding used in the file.

    Returns:
        PostDefinition: The data extracted from the file

    Raises:
        PostError: If any data fails to correctly validate
    """
    md = markdown.Markdown(extensions=['markdown_extra.summary',
                                       'markdown_extra.meta'])

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

    return PostDefinition(
        id=meta['id'],
        title=meta['title'],
        slug=meta['slug'],
        summary=md.summary,
        date=meta.get('date', date.today()),
        category=meta['category'],
        markdown=md_content,
        html=html_content)
