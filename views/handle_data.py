import copy

from flask import Blueprint, render_template, url_for, request
from werkzeug.utils import redirect

from helpers.database import check_database, live_scraping

bp = Blueprint("handle_data", __name__)


@bp.route("/handle_data", methods=["POST", "GET"])
def handle_data():
    if request.method == "GET":
        return redirect(url_for("scraper.scraper"))

    task_title = request.form.get("title")
    task_author = request.form.get("author")
    if request.form.get("submit_button") == "Check DB":
        new_lista = check_database(task_author, task_title)
        if new_lista:
            return render_template("index.html", lista=new_lista)
        else:
            return render_template(
                "index.html",
                lista=new_lista,
                author_name=task_author,
                book_title=task_title,
                show_button=True,
            )

    else:
        new_lista = live_scraping(task_author, task_title)
        change_list = copy.deepcopy(new_lista)
        for d in change_list:
            d.update((k, ", ".join(map(str, v))) for k, v in d.items() if k == "author")
            d.update(
                (k, "https://znanje.hr/")
                for k, v in d.items()
                if k == "page" and v == 2
            )
            d.update(
                (k, "https://knjiga.hr/")
                for k, v in d.items()
                if k == "page" and v == 5
            )
            d.update(
                (k, "https://mozaik-knjiga.hr/")
                for k, v in d.items()
                if k == "page" and v == 3
            )

        return render_template("index.html", lista=change_list)
