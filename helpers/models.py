from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


book_authors = db.Table(
    "book_authors",
    db.Column("book_id", db.Integer, db.ForeignKey("books.id")),
    db.Column("author_id", db.Integer, db.ForeignKey("authors.id")),
)


class Authors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    def __repr__(self):
        return '<Authors %r>' % self.id

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    book_authors_connection = db.relationship(
        "Authors", secondary=book_authors, backref=db.backref("auth", lazy="dynamic")
    )
    offer = db.relationship("Offers", backref=db.backref("off"))
    def __repr__(self):
        return '<Books %r>' % self.id

class Offers(db.Model):
    link = db.Column(db.String(200), primary_key=True)
    price = db.Column(db.String(200))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    pages_id = db.Column(db.Integer, db.ForeignKey("pages.id"))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Offers %r>" % self.link


class Pages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(200))
    name = db.Column(db.String(200))
    image = db.Column(db.String(200))
    offer = db.relationship("Offers", backref=db.backref("offp"))

    def __repr__(self):
        return "<Pages %r>" % self.id


class Oglasi(db.Model):
    __bind_key__ = "oglasnik"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    price = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    body = db.Column(db.String(300))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    img_url = db.Column(db.String(30))

    def __repr__(self):
        return "<Oglasi %r>" % self.id


class Users(db.Model, UserMixin):
    __bind_key__ = "oglasnik"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    email = db.Column(db.String(30))
    username = db.Column(db.String(30))
    password = db.Column(db.String(120))
    ogl = db.relationship("Oglasi", backref=db.backref("ogl_user"))

    def __repr__(self):
        return '<Users %r>' % self.id



