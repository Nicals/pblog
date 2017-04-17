"""Models serialization is defined in this module
"""

from marshmallow import Schema, fields


class TopicSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class PostSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    slug = fields.String()
    topic = fields.Nested(TopicSchema)
    published_date = fields.Date()
