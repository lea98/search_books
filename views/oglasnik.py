from flask import Blueprint, render_template
from sqlalchemy import desc

from helpers.models import Oglasi, db, Users

bp = Blueprint("oglasnik", __name__)


@bp.route("/oglasnik", methods=["GET", "POST"])
def oglasnik():
    oglasi = (
        db.session.query(
            Oglasi.title,
            Oglasi.body,
            Oglasi.price,
            Oglasi.date_created,
            Oglasi.img_url,
            Users.email,
        )
        .order_by(desc(Oglasi.date_created))
        .join(Users, Users.id == Oglasi.user_id)
        .all()
    )
    return render_template("oglasnik.html", oglasi_list=oglasi)
