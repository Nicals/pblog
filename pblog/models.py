from pblog.core import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{} {}:{}>'.format(self.__class__.__name__, self.id, self.name)


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text(), default='', nullable=False)
    published_date = db.Column(db.Date(), nullable=False)
    md_content = db.Column(db.Text(), nullable=False)
    html_content = db.Column(db.Text(), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship(
        'Category', backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return '<{} {}:{}>'.format(self.__class__.__name__, self.id, self.name)
