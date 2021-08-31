from flask import Blueprint, url_for
from flask_login import login_required, logout_user
from werkzeug.utils import redirect


bp = Blueprint("logout", __name__)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing.index"))
