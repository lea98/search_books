import os

from flask import Blueprint, render_template, current_app, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from werkzeug.utils import redirect, secure_filename
from datetime import datetime
from wtforms import StringField, TextAreaField, FileField
from wtforms.validators import InputRequired, Length

from helpers.models import db, Oglasi

bp = Blueprint("add_oglas", __name__)


class OglasForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(min=1, max=20)])
    body = TextAreaField("Text", validators=[InputRequired(), Length(min=1, max=200)])
    img_url = FileField(
        "",
        validators=[
            FileRequired(),
        ],
    )
    price = StringField("Price", validators=[InputRequired(), Length(min=1, max=10)])


@bp.route("/add_oglas", methods=["GET", "POST"])
@login_required
def add_oglas():
    form = OglasForm()
    if form.validate_on_submit():
        f = form.img_url.data
        filename = secure_filename(form.img_url.data.filename)
        filename = datetime.strftime(datetime.now(), "%M%S") + filename
        f.save(os.path.join(current_app.config["UPLOADED_IMAGES_DEST"], filename))

        title = form.title.data
        body = form.body.data
        price = form.price.data

        new_oglas = Oglasi(
            title=title,
            body=body,
            user_id=current_user.id,
            date_created=datetime.now().replace(microsecond=0),
            price=price,
            img_url=filename,
        )
        db.session.add(new_oglas)
        db.session.commit()

        return redirect(url_for("dashboard.dashboard"))

    return render_template("dashboard.html", form=form)
