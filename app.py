import os
from flask import Flask

from flask_login import (
    LoginManager,
)
from flask_bootstrap import Bootstrap
from flask_uploads import configure_uploads, IMAGES, UploadSet

from helpers.models import Users,Pages
from views import blueprints
from helpers.models import db

LOGOS_FOLDER = os.path.join("static", "logos")
UPLOADS_FOLDER = os.path.join("static", "uploads")

app = Flask(__name__)  # setup app, name referencing this file
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
bootstrap = Bootstrap(app)

# LOCAL TESTING
# app.config[
#     "SQLALCHEMY_DATABASE_URI"
# ] = "postgresql://postgres:books1234@localhost/bookscraper"
# app.config["SQLALCHEMY_BINDS"] = {
#     "oglasnik": "postgresql://postgres:books1234@localhost/oglasnik"
# }

DATABASE_URL = os.environ.get('DATABASE_URL').replace('postgres', 'postgresql')
HEROKU_POSTGRESQL_CHARCOAL_URL = os.environ.get('HEROKU_POSTGRESQL_CHARCOAL_URL').replace('postgres', 'postgresql')
SQLALCHEMY_DATABASE_URI = DATABASE_URL
app.config['SQLALCHEMY_BINDS'] = {
    'oglasnik': HEROKU_POSTGRESQL_CHARCOAL_URL,
}

app.config["UPLOAD_FOLDER"] = LOGOS_FOLDER

app.config["UPLOADED_IMAGES_DEST"] = UPLOADS_FOLDER
images = UploadSet("images", IMAGES)
configure_uploads(app, images)

# app.config.from_object(__name__)

db.init_app(app)

# FOR SETTING UP FIRST TIME
db.create_all()
db.session.commit()

if not (db.session.execute("select count(*) from pages").first())[0]:
    page1 = Pages(id=1, link="https://www.barnesandnoble.com/", name="Barnes & Noble", image="barnesandnoble.jpg")
    page2 = Pages(id=2, link="https://znanje.hr/", name="Znanje", image="znanje.jpg")
    page3 = Pages(id=3, link="https://mozaik-knjiga.hr/", name="Mozaik Knjiga", image="mozaik.jpg")
    page4 = Pages(id=4, link="https://www.ljevak.hr/", name="Ljevak", image="ljevak.jpg")
    page5 = Pages(id=5, link="https://knjiga.hr/", name="Knjiga", image="knjiga.jpg")
    db.session.add(page1)
    db.session.add(page2)
    db.session.add(page3)
    db.session.add(page4)
    db.session.add(page5)
    db.session.commit()

for blue in blueprints:
    app.register_blueprint(blue.bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


if __name__ == "__main__":
    app.run(debug=True)
