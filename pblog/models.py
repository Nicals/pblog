from pblog.core import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    slug = db.Column(db.String(50))

    def __init__(self, name, slug):
        self.name = name
        self.slug = slug

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{} {}:{}>'.format(self.__class__.__name__, self.id, self.name)


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    slug = db.Column(db.String(255))
    summary = db.Column(db.Text())
    published_date = db.Column(db.Date(), nullable=False)
    md_content = db.Column(db.Text())
    html_content = db.Column(db.Text())
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship(
        'Category', backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title, slug, published_date, summary='', md_content='',
                 html_content='', category=None):
        self.title = title
        self.slug = slug
        self.summary = summary
        self.published_date = published_date
        self.md_content = md_content
        self.html_content = html_content
        self.category = category

    def __repr__(self):
        return '<{} {}:{}>'.format(self.__class__.__name__, self.id, self.name)
