import copy
import os
import time

import flask
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session, after_this_request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
from urllib.parse import urlparse, urljoin

from flask_wtf.file import FileRequired
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from beautifulsoup_bookstores.znanje import znanje
# from bookstores.eurospanbookstore import eurospanbookstore
from helpers.general import match_author
from selenium_bookstores.knjiga import knjiga
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, FileField, MultipleFileField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import email_validator
from flask_bootstrap import Bootstrap
from functools import wraps
from flask_uploads import configure_uploads, IMAGES, UploadSet #https://stackoverflow.com/questions/61628503/flask-uploads-importerror-cannot-import-name-secure-filename

LOGOS_FOLDER = os.path.join('static', 'logos')
UPLOADS_FOLDER =  os.path.join('static', 'uploads')

app = Flask(__name__)  # setup app, name referencing this file
app.config['SECRET_KEY'] = 'd64938c6ccdb42fcafaa7ff467f309bd'
bootstrap = Bootstrap(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test3.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///bookoffers.db'

SQLALCHEMY_BINDS = {
    'oglasnik': 'sqlite:///oglasnik.db',
}

app.config['UPLOAD_FOLDER'] = LOGOS_FOLDER

app.config['UPLOADED_IMAGES_DEST'] = UPLOADS_FOLDER
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

app.config.from_object(__name__)

db = SQLAlchemy(app) #initialize database with settings from our app
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



book_authors = db.Table('book_authors',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id'))

)

class Authors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    book_authors_connection = db.relationship('Authors', secondary=book_authors, backref =db.backref('auth',lazy='dynamic'))
    offer = db.relationship('Offers',backref =db.backref('off'))


class Offers(db.Model):
    link = db.Column(db.String(200), primary_key=True)
    price = db.Column(db.String(200))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    pages_id = db.Column(db.Integer, db.ForeignKey('pages.id'))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)


    #function that will return a string every time we add new element (pari nebitno)
    def __repr__(self):
        return '<Task %r>' % self.id

class Pages(db.Model):
    id = db.Column(db.Integer, primary_key=True)#column
    link = db.Column(db.String(200))
    name = db.Column(db.String(200))
    image = db.Column(db.String(200))
    offer = db.relationship('Offers',backref =db.backref('offp'))

    #function that will return a string every time we add new element (pari nebitno)
    def __repr__(self):
        return '<Task %r>' % self.id


class Oglasi(db.Model):
    __bind_key__ = 'oglasnik'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    price = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.String(300))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    img_url = db.Column(db.String(30))
    def __repr__(self):
        return '<Oglasi %r>' % self.id

class Users(db.Model, UserMixin):
    __bind_key__ = 'oglasnik'
    id = db.Column(db.Integer, primary_key=True)#column
    name = db.Column(db.String(30))
    email = db.Column(db.String(30))
    username = db.Column(db.String(30))
    password = db.Column(db.String(30))
    ogl = db.relationship('Oglasi',backref =db.backref('ogl_user'))


db.create_all()
db.session.commit()

# if not (db.session.execute("select count(*) from pages").first())[0]:
#     page1 = Pages(id=1, link="https://www.barnesandnoble.com/", name="Barnes & Noble", image="barnesandnoble.jpg")
#     page2 = Pages(id=2, link="https://znanje.hr/", name="Znanje", image="znanje.jpg")
#     page3 = Pages(id=3, link="https://mozaik-knjiga.hr/", name="Mozaik Knjiga", image="mozaik.jpg")
#     page4 = Pages(id=4, link="https://www.ljevak.hr/", name="Ljevak", image="ljevak.jpg")
#     page5 = Pages(id=5, link="https://knjiga.hr/", name="Knjiga", image="knjiga.jpg")
#     db.session.add(page1)
#     db.session.add(page2)
#     db.session.add(page3)
#     db.session.add(page4)
#     db.session.add(page5)
#     db.session.commit()


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('landing.html') #base.html 1 master html, skeleton for other to inherit


@app.route('/scraper', methods=['GET','POST'])
def scraper():
    return render_template('scraper.html') #base.html 1 master html, skeleton for other to inherit


@app.route('/oglasnik', methods=['GET','POST'])
def oglasnik():

    oglasi = db.session.query(Oglasi.title, Oglasi.body, Oglasi.price, Oglasi.date_created, Oglasi.img_url, Users.email).order_by(desc(Oglasi.date_created)).join(Users, Users.id == Oglasi.user_id).all()
    return render_template('oglasnik.html', oglasi_list=oglasi) #base.html 1 master html, skeleton for other to inherit


######################################################################################################################################
@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=3, max=50)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=15)])
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=3, max=50)])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                print(form.remember.data)
                login_user(user, remember=True)
                next = flask.request.args.get('next')
                if not is_safe_url(next):
                    return flask.abort(400)
                return redirect(next or url_for('dashboard'))

        return render_template('login.html', form=form, invalid_pass=True)

    return render_template('login.html', form=form, invalid_pass=False)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        exists_user_username = db.session.query(Users).filter(Users.username == form.username.data).first() is not None
        print(exists_user_username)
        if exists_user_username:
            return render_template('register.html', form=form, message="Username already exists")
        exists_user_mail = db.session.query(Users).filter(Users.email == form.email.data).first() is not None
        if exists_user_mail:
            return render_template('register.html', form=form, message="Email already exists")

        new_user = Users(username=form.username.data, email=form.email.data, password=hashed_password, name=form.name.data)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)



@app.route('/dashboard')
@login_required
def dashboard():
    form = OglasForm()
    oglasi = db.session.query(Oglasi.id, Oglasi.title, Oglasi.price, Oglasi.body, Oglasi.img_url, Oglasi.date_created).order_by(desc(Oglasi.date_created)).filter(Oglasi.user_id == current_user.id).all()

    return render_template('dashboard.html', oglasi_list = oglasi, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
##########################################################################################################################################

class OglasForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(min=1, max=20)])
    body = TextAreaField('Text', validators=[InputRequired(), Length(min=1, max=200)])
    img_url = FileField("",validators=[ FileRequired(),])
    price = StringField('Price', validators=[InputRequired(), Length(min=1, max=10)])


# Article Form Class
class OglasFormEdit(FlaskForm):
    title = StringField('New title', validators=[Length(min=1, max=20)])
    body = TextAreaField('New text', validators=[Length(min=1, max=200)])
    img_url = FileField("")
    price = StringField('New price', validators=[Length(min=1, max=10)])


# Add Oglas
@app.route('/add_oglas', methods=['GET', 'POST'])
@login_required
def add_oglas():
    form = OglasForm()
    if form.validate_on_submit():

        f = form.img_url.data
        filename = secure_filename(form.img_url.data.filename)
        filename = datetime.strftime(datetime.now(),"%M%S") + filename
        f.save(os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename))

        title = form.title.data
        body = form.body.data
        price = form.price.data


        new_oglas = Oglasi(
                         title=title,
                         body=body, user_id=current_user.id, date_created=datetime.now().replace(microsecond=0), price=price, img_url=filename)
        db.session.add(new_oglas)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', form=form)


# Delete Oglas
@app.route('/delete_oglas/<string:id>', methods=['POST'])
@login_required
def delete_oglas(id):
    filename = db.session.query(Oglasi.img_url).filter(Oglasi.id==id).first()
    os.remove(os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename[0]))

    Oglasi.query.filter_by(id=id).delete()
    db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/edit_oglas/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_oglas(id):
    form = OglasFormEdit()
    oglas = db.session.query(Oglasi).filter_by(id=id).first()
    print('111111')
    print((db.session.query(Oglasi).filter_by(id=id).first()).id)
    print('111111')


    # makla sam     {{ form.hidden_tag() }} ko dashboard.html da se razlikuje, a da nije token u urlu
    if request.method == 'POST' and form.validate():
        db.session.commit()  #https://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information


        title = form.title.data
        body = form.body.data
        price = form.price.data

        if price:
            oglas.price = price
        if title:
            oglas.title=title
        if body:
            oglas.body = body
        if form.img_url.data:
            f = form.img_url.data
            filename = secure_filename(form.img_url.data.filename)
            filename = datetime.strftime(datetime.now(), "%M%S") + filename
            f.save(os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename))
            oglas.img_url = filename
        if price or title or body or form.img_url.data:
            oglas.date_created =datetime.now().replace(microsecond=0)

        db.session.commit()

        return redirect(url_for('dashboard'))
    return render_template('edit_oglas.html', form=form, oglas=oglas)

####################################################################################################################################################
@app.route('/handle_data', methods=['POST','GET'])
def handle_data():
    if request.method == 'GET':
        return redirect(url_for('scraper'))

    task_title = request.form.get('title') #u ndex.html form name=content
    task_author = request.form.get('author') #u ndex.html form name=content
    if request.form.get('submit_button') == 'Check DB':
        new_lista = check_database(task_author, task_title)
        if new_lista:
            return render_template('index.html', lista=new_lista)  # base.html 1 master html, skeleton for other to inherit
        else:
            return render_template('index.html', lista=new_lista, author_name=task_author, book_title=task_title, show_button=True)

    else:
        new_lista = live_scraping(task_author, task_title)
        change_list = copy.deepcopy(new_lista)
        for d in change_list:
            d.update((k, ', '.join(map(str, v))) for k, v in d.items() if k == 'author')
            d.update((k, "https://znanje.hr/") for k, v in d.items() if k == 'page' and v == 2)
            d.update((k, "https://knjiga.hr/") for k, v in d.items() if k == 'page' and v == 5)

        return render_template('index.html', lista=change_list)  # base.html 1 master html, skeleton for other to inherit

def check_database(task_author, task_title):
    new_lista=[]
    book_exists = db.session.query(Books.id).filter(Books.title == task_title).all()
    result = ""
    if task_title and task_author:
        result = db.session.execute(f"""SELECT offers.link, offers.price, offers.book_id, offers.pages_id
                    FROM offers
                    INNER JOIN books ON offers.book_id=books.id Where books.id IN (SELECT b.id
        FROM books b
        JOIN book_authors ba ON b.id = ba.book_id
        JOIN authors a ON ba.author_id = a.id
        WHERE a.name LIKE "%{task_author}%" AND b.title LIKE "{task_title}%");""")

    if not task_title and not task_author:
        pass

    elif not task_title:
        result = db.session.execute(f"""SELECT offers.link, offers.price, offers.book_id, offers.pages_id
            FROM offers
            INNER JOIN books ON offers.book_id=books.id Where books.id IN (SELECT b.id
FROM books b
JOIN book_authors ba ON b.id = ba.book_id
JOIN authors a ON ba.author_id = a.id
WHERE a.name LIKE "%{task_author}%");""")

    elif not task_author:
        result = db.session.execute(f"""SELECT offers.link, offers.price, offers.book_id, offers.pages_id
            FROM offers
            INNER JOIN books ON offers.book_id=books.id Where books.id IN (SELECT b.id
FROM books b
JOIN book_authors ba ON b.id = ba.book_id
JOIN authors a ON ba.author_id = a.id
WHERE b.title LIKE "{task_title}%");""")

    if result:
        offers = result.mappings().all()
        for offer in offers:
            book_full_name = db.session.query(Books.title).filter(Books.id == offer['book_id']).first()
            authors_for_book = db.session.execute(f"""SELECT authors.name
    FROM authors
    JOIN book_authors ON authors.id = book_authors.author_id
    JOIN books ON book_authors.book_id = {offer['book_id']} GROUP BY authors.name""")
            authors_to_display = ", ".join(i['name'] for i in (authors_for_book.mappings().all()))

            page_link = db.session.query(Pages.link, Pages.image).filter(Pages.id == offer['pages_id']).first()
            new_lista.append({'price': offer['price'], 'author': authors_to_display, 'title': book_full_name[0],
                              'link': page_link[0] + offer['link'],
                              'page': page_link[0],
                              'page_logo': os.path.join(app.config['UPLOAD_FOLDER'], page_link[1])})

    return new_lista


def live_scraping(task_author, task_title):
    new_lista=[]
    # znanje_list = znanje(task_title, task_author)
    # znanje_list = match_author(znanje_list, task_author, task_title)
    # print(znanje_list)
    # if znanje_list:
    #     for item in znanje_list:
    #         item['page_logo']=os.path.join(app.config['UPLOAD_FOLDER'], 'znanje.jpg')
    #
    # knjiga_list = knjiga(task_title, task_author)
    # knjiga_list = match_author(knjiga_list, task_author, task_title)
    # if knjiga_list:
    #     for item in knjiga_list:
    #         item['page_logo']=os.path.join(app.config['UPLOAD_FOLDER'], 'knjiga.png')
    #
    # new_lista =  znanje_list + knjiga_list
    print('LIVE scrr')
    #new_lista =[{'price': '88,00 kn', 'author': ['Ivan Kušan'], 'title': 'Ljubav ili smrt', 'link': 'https://znanje.hr/product/ljubav-ili-smrt/201846', 'page': 2, 'page_logo': 'static\\logos\\znanje.jpg'},  {'price':'35,00 kn', 'author': ['Ivan Kušan'], 'title': 'Koko i duhovi', 'link': 'https://knjiga.hr/koko-i-duhovi-ivan-kusan-1-5', 'page': 5, 'page_logo': 'static\\logos\\knjiga.png'}]
    @after_this_request
    def save_to_db_after_scraping(response):
        for item in new_lista:
            exists_in = check_if_exists_in_table(item)
            if not exists_in:
                db.session.execute(f"""insert into books values (null,"{item['title']}")""")
                book_id = db.session.execute("SELECT LAST_INSERT_ROWID()")
                book_id_num = list(book_id)[0][0]
                for auth in item['author']:
                    print(auth)
                    db.session.execute(f'''INSERT INTO authors (name)
                                    SELECT "{auth}"
                                    FROM authors
                                    WHERE NOT EXISTS (SELECT id FROM authors WHERE name="{auth}")
                                    LIMIT 1;
                                    ''')
                    auth_is_there_list = db.session.execute(f'''select id from authors where name="{auth}"''')
                    auth_id_num = auth_is_there_list.fetchone()[0]

                    db.session.execute(f"""insert into book_authors values ({book_id_num},{auth_id_num})""")
            else:
                book_id_num = exists_in


            db.session.execute(f"""INSERT INTO offers (link,price,book_id,pages_id,date_added)
                    VALUES ("{item['link']}","{item['price']}",{book_id_num},"{item['page']}","{datetime.utcnow()}")
                    ON CONFLICT(link) DO UPDATE SET price = ("{item['price']}"),date_added=("{datetime.utcnow()}");""")
            #db.session.commit()
        return response

    return new_lista


def check_if_exists_in_table(item):
    all_books_with_that_name = db.session.execute(f"""select id from books where title = '{item['title']}'""")
    for book_id in list(all_books_with_that_name):
        book_authors_match = db.session.execute(f"""select author_id from book_authors where book_id = {book_id[0]}""")
        for author_name in list(book_authors_match):
            authors_match = db.session.execute(f"""select name from authors where id = ({author_name[0]})""")
            if not list(authors_match)[0][0] in item['author']:
                break
            return book_id[0]

    return False

if __name__ == "__main__":
    app.run(debug=True)