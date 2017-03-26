"""Models serialization is defined in this module
"""

from marshmallow.fields import Nested
from marshmallow_sqlalchemy import ModelSchema

from flask_pblog.models import Category, Post


class CategorySchema(ModelSchema):
    class Meta:
        fields = ('id', 'name')
        model = Category


class PostSchema(ModelSchema):
    category = Nested(CategorySchema)

    class Meta:
        fields = ('id', 'title', 'slug', 'category', 'published_date')
        model = Post
