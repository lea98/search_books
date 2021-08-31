import os

from flask import Blueprint, render_template, current_app, url_for, request
from flask_login import login_required
from flask_wtf import FlaskForm
from werkzeug.utils import redirect, secure_filename
from datetime import datetime
from wtforms import StringField, TextAreaField, FileField

from helpers.models import db, Oglasi

bp = Blueprint("edit_oglas", __name__)


class OglasFormEdit(FlaskForm):
    title = StringField("New title")
    body = TextAreaField("New text")
    img_url = FileField("")
    price = StringField("New price")


@bp.route("/edit_oglas/<string:id>", methods=["GET", "POST"])
@login_required
def edit_oglas(id):
    form = OglasFormEdit()
    oglas = db.session.query(Oglasi).filter_by(id=id).first()

    if request.method == "POST" and form.validate():
        db.session.commit()

        title = form.title.data
        body = form.body.data
        price = form.price.data

        if price:
            oglas.price = price
        if title:
            oglas.title = title
        if body:
            oglas.body = body
        if form.img_url.data:
            f = form.img_url.data
            filename = secure_filename(form.img_url.data.filename)
            filename = datetime.strftime(datetime.now(), "%M%S") + filename
            f.save(os.path.join(current_app.config["UPLOADED_IMAGES_DEST"], filename))
            oglas.img_url = filename
        if price or title or body or form.img_url.data:
            oglas.date_created = datetime.now().replace(microsecond=0)

        db.session.commit()

        return redirect(url_for("dashboard.dashboard"))
    return render_template("edit_oglas.html", form=form, oglas=oglas)
