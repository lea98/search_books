import os

from flask import Blueprint, current_app, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from helpers.models import db, Oglasi

bp = Blueprint("delete_oglas", __name__)


@bp.route("/delete_oglas/<string:id>", methods=["POST"])
@login_required
def delete_oglas(id):
    filename = db.session.query(Oglasi.img_url).filter(Oglasi.id == id).first()
    os.remove(os.path.join(current_app.config["UPLOADED_IMAGES_DEST"], filename[0]))

    Oglasi.query.filter_by(id=id).delete()
    db.session.commit()

    return redirect(url_for("dashboard.dashboard"))
