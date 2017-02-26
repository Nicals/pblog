from pblog.core import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    slug = db.Column(db.String(50))

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{} {}:{}>'.format(self.__name__, self.id, self.name)


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    slug = db.Column(db.String(255))
    summary = db.Column(db.Text())
    md_content = db.Column(db.Text())
    html_content = db.Column(db.Text())
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship(
        'Category', backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return '<{} {}:{}>'.format(self.__name__, self.id, self.name)
