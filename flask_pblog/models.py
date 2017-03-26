# from pblog.core import db
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    slug = Column(String(50), nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{} {}:{}>'.format(self.__class__.__name__, self.id, self.name)


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    summary = Column(Text(), default='', nullable=False)
    published_date = Column(Date(), nullable=False)
    md_content = Column(Text(), nullable=False)
    html_content = Column(Text(), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship(
        'Category', backref=backref('posts', lazy='dynamic'))

    def __repr__(self):
        return '<{} {}:{}>'.format(self.__class__.__name__, self.id, self.title)
