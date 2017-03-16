"""Models serialization is defined in this module
"""

from pblog.core import marshmallow
from pblog.models import Category, Post


class CategorySchema(marshmallow.ModelSchema):
    class Meta:
        fields = ('id', 'name')
        model = Category


class PostSchema(marshmallow.ModelSchema):
    category = marshmallow.Nested(CategorySchema)

    class Meta:
        fields = ('id', 'title', 'slug', 'category', 'published_date')
        model = Post
