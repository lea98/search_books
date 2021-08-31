from flask import Blueprint, render_template, url_for
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from helpers.models import Users, db

bp = Blueprint("register", __name__)


class RegisterForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[InputRequired(), Email(message="Invalid email"), Length(max=50)],
    )
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=3, max=15)]
    )
    name = StringField("Name", validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=3, max=50)]
    )


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method="sha256")
        exists_user_username = (
            db.session.query(Users).filter(Users.username == form.username.data).first()
            is not None
        )
        if exists_user_username:
            return render_template(
                "register.html", form=form, message="Username already exists"
            )
        exists_user_mail = (
            db.session.query(Users).filter(Users.email == form.email.data).first()
            is not None
        )
        if exists_user_mail:
            return render_template(
                "register.html", form=form, message="Email already exists"
            )

        new_user = Users(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            name=form.name.data,
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login.login"))

    return render_template("register.html", form=form)
