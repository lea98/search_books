from flask import Blueprint, render_template

bp = Blueprint("scraper", __name__)


@bp.route("/scraper", methods=["GET", "POST"])
def scraper():
    return render_template("scraper.html")
