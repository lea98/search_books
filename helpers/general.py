def match_author(lista, author=None, title=None):
    if author and title:
        res = [i for i in lista if (author in i['author'] and i['title'] == title)]
    elif title:
        res = [i for i in lista if (i['title'] == title)]
    else:
        res = [i for i in lista if (author in i['author'])]

    return res
