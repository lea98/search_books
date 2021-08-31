import os


from datetime import datetime, timedelta

from flask import after_this_request, current_app

from beautifulsoup_bookstores.znanje import znanje
from helpers.general import match_author
from helpers.models import Books, Pages, db
from selenium_bookstores.knjiga import knjiga
from selenium_bookstores.mozaik import mozaik


def check_database(task_author, task_title):
    new_lista = []
    book_exists = db.session.query(Books.id).filter(Books.title == task_title).all()
    result = ""
    if task_title and task_author:
        result = db.session.execute(
            """SELECT offers.link, offers.price, offers.book_id, offers.pages_id,offers.date_added
                    FROM offers
                    INNER JOIN books ON offers.book_id=books.id Where books.id IN (SELECT b.id
        FROM books b
        JOIN book_authors ba ON b.id = ba.book_id
        JOIN authors a ON ba.author_id = a.id
        WHERE a.name = :autname AND b.title = :title);""",
            {"autname": task_author, "title": task_title},
        )

    if not task_title and not task_author:
        pass

    elif not task_title:
        result = db.session.execute(
            """SELECT offers.link, offers.price, offers.book_id, offers.pages_id,offers.date_added
            FROM offers
            INNER JOIN books ON offers.book_id=books.id WHERE books.id IN (SELECT b.id
FROM books b
JOIN book_authors ba ON b.id = ba.book_id
JOIN authors a ON ba.author_id = a.id
WHERE a.name = :autname
);""",
            {"autname": task_author},
        )

    elif not task_author:
        result = db.session.execute(
            """SELECT offers.link, offers.price, offers.book_id, offers.pages_id, offers.date_added
            FROM offers
            INNER JOIN books ON offers.book_id=books.id Where books.id IN (SELECT b.id
FROM books b
JOIN book_authors ba ON b.id = ba.book_id
JOIN authors a ON ba.author_id = a.id
WHERE b.title = :title);""",
            {"title": task_title},
        )
    if result:
        offers = result.mappings().all()
        for offer in offers:
            check_date = (
                datetime.strptime(offer.date_added.split(" ")[0], "%Y-%m-%d")
                if isinstance(offer.date_added, str)
                else offer.date_added
            )  # fix
            if check_date <= (datetime.now() - timedelta(weeks=1)):
                continue
            book_full_name = (
                db.session.query(Books.title)
                .filter(Books.id == offer["book_id"])
                .first()
            )
            authors_for_book = db.session.execute(
                """SELECT authors.name
    FROM authors
    JOIN book_authors ON authors.id = book_authors.author_id
    JOIN books ON book_authors.book_id = :bookid GROUP BY authors.name""",
                {"bookid": offer["book_id"]},
            )
            authors_to_display = ", ".join(
                i["name"] for i in (authors_for_book.mappings().all())
            )
            page_link = (
                db.session.query(Pages.link, Pages.image)
                .filter(Pages.id == offer["pages_id"])
                .first()
            )
            new_lista.append(
                {
                    "price": offer["price"],
                    "author": authors_to_display,
                    "title": book_full_name[0],
                    "link": page_link[0] + offer["link"],
                    "page": page_link[0],
                    "page_logo": os.path.join(
                        current_app.config["UPLOAD_FOLDER"], page_link[1]
                    ),
                }
            )

    return new_lista


def live_scraping(task_author, task_title):
    new_lista = []
    znanje_list = znanje(task_title, task_author)
    znanje_list = match_author(znanje_list, task_author, task_title)
    if znanje_list:
        for item in znanje_list:
            item["page_logo"] = os.path.join(
                current_app.config["UPLOAD_FOLDER"], "znanje.jpg"
            )

    knjiga_list = knjiga(task_title, task_author)
    knjiga_list = match_author(knjiga_list, task_author, task_title)
    if knjiga_list:
        for item in knjiga_list:
            item["page_logo"] = os.path.join(
                current_app.config["UPLOAD_FOLDER"], "knjiga.jpg"
            )

    mozaik_list = mozaik(task_title, task_author)
    mozaik_list = match_author(mozaik_list, task_author, task_title)
    if mozaik_list:
        for item in mozaik_list:
            item["page_logo"] = os.path.join(
                current_app.config["UPLOAD_FOLDER"], "mozaik.jpg"
            )

    new_lista = mozaik_list + knjiga_list + znanje_list

    # new_lista =[{'price': '88,00 kn', 'author': ['Ivan Kušan'], 'title': 'Ljubav ili smrt', 'link': 'https://znanje.hr/product/ljubav-ili-smrt/201846', 'page': 2, 'page_logo': 'static\\logos\\znanje.jpg'},  {'price':'35,00 kn', 'author': ['Ivan Kušan'], 'title': 'Koko i duhovi', 'link': 'https://knjiga.hr/koko-i-duhovi-ivan-kusan-1-5', 'page': 5, 'page_logo': 'static\\logos\\knjiga.png'}]
    @after_this_request
    def save_to_db_after_scraping(response):
        for item in new_lista:
            exists_in = check_if_exists_in_table(item)
            titles = item["title"].replace("'", "''")
            if not exists_in:
                book_id = db.session.execute(
                    """insert into books values (DEFAULT, :titles) RETURNING id;""",
                    {"titles": titles},
                )
                book_id_num = book_id.first()[0]
                for auth in item["author"]:
                    auth_is_there_list = db.session.execute(
                        """select id from authors where name = :autname;""",
                        {"autname": auth},
                    ).fetchone()
                    if not auth_is_there_list:
                        auth_id_num = db.session.execute(
                            """insert into authors values (DEFAULT,:autname) RETURNING id;""",
                            {"autname": auth},
                        ).first()[0]
                    else:
                        auth_id_num = auth_is_there_list[0]
                    db.session.execute(
                        """insert into book_authors values (:bookid,:autid);""",
                        {"bookid": book_id_num, "autid": auth_id_num},
                    )
            else:
                book_id_num = exists_in
            new_link = (
                item["link"]
                .replace("https://mozaik-knjiga.hr/", "")
                .replace("https://znanje.hr/", "")
                .replace("https://knjiga.hr/", "")
            )
            db.session.execute(
                """INSERT INTO offers (link,price,book_id,pages_id,date_added)
                    VALUES (:newlink,:price,:bookid,:page,:dateadd)
                    ON CONFLICT (link) DO UPDATE SET (price, date_added) = (:price,:dateadd);""",
                {
                    "newlink": new_link,
                    "price": item["price"],
                    "bookid": book_id_num,
                    "page": item["page"],
                    "dateadd": datetime.utcnow(),
                },
            )

            db.session.commit()
        return response

    return new_lista


def check_if_exists_in_table(item):
    # title_escape_quote = item["title"].replace("'", "''")
    all_books_with_that_name = db.session.execute(
        "select id from books where title = :title", {"title": item["title"]}
    )
    for book_id in list(all_books_with_that_name):
        book_authors_match = db.session.execute(
            "select author_id from book_authors where book_id = :bookid",
            {"bookid": book_id[0]},
        )
        for author_name in list(book_authors_match):
            authors_match = db.session.execute(
                "select name from authors where id = :autname",
                {"autname": author_name[0]},
            )
            if not list(authors_match)[0][0] in item["author"]:
                break
            return book_id[0]

    return False
