"""Models serialization is defined in this module
"""

from marshmallow import Schema, fields


class CategorySchema(Schema):
    id = fields.Number()
    name = fields.String()


class PostSchema(Schema):
    id = fields.Number()
    title = fields.String()
    slug = fields.String()
    category = fields.Nested(CategorySchema)
    published_date = fields.Date()
