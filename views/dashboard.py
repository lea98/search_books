from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import desc

from helpers.models import Oglasi, db
from views.add_oglas import OglasForm

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
@login_required
def dashboard():
    form = OglasForm()
    oglasi = (
        db.session.query(
            Oglasi.id,
            Oglasi.title,
            Oglasi.price,
            Oglasi.body,
            Oglasi.img_url,
            Oglasi.date_created,
        )
        .order_by(desc(Oglasi.date_created))
        .filter(Oglasi.user_id == current_user.id)
        .all()
    )

    return render_template("dashboard.html", oglasi_list=oglasi, form=form)
