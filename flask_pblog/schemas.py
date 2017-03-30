"""Models serialization is defined in this module
"""

from marshmallow import Schema, fields


class CategorySchema(Schema):
    id = fields.Integer()
    name = fields.String()


class PostSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    slug = fields.String()
    category = fields.Nested(CategorySchema)
    published_date = fields.Date()
