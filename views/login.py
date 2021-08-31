import flask
from flask import Blueprint, url_for, render_template, request
from flask_login import login_user
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash
from urllib.parse import urlparse, urljoin

from helpers.models import Users
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length

bp = Blueprint("login", __name__)


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=3, max=15)]
    )
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=3, max=50)]
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=True)  # maybe add option
                next = flask.request.args.get("next")
                if not is_safe_url(next):
                    return flask.abort(400)
                return redirect(next or url_for("dashboard.dashboard"))

        return render_template("login.html", form=form, invalid_pass=True)

    return render_template("login.html", form=form, invalid_pass=False)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc
