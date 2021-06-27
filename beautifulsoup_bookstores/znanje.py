import time

from bs4 import BeautifulSoup
import requests



def znanje(task_cont, task_title):
    hdr = {'Accept': 'text/html,application/xhtml+xml,*/*',
           "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36"}

    if task_cont and task_title:
        to_url = (task_cont + ' ' + task_title).replace(' ', '+')
    elif task_cont:
        to_url = task_cont.replace(' ', '+')
    else:
        to_url = task_title.replace(' ', '+')

    url = f"https://znanje.hr/pretraga?query={to_url}"

    page = requests.get(url, headers=hdr)

    time.sleep(5)
    soup = BeautifulSoup(page.content, 'html.parser')

    # data = soup.findAll('div', attrs={'class','product-card'})
    price = soup.findAll('h4', attrs={'class', 'product-price'})
    title_meta = soup.findAll('h3', attrs={'class', 'product-title'})

    authors_meta = soup.findAll('p', attrs={'class', 'product-author'})

    lista = []

    for (i, j, k) in zip(price, authors_meta, title_meta):
        lista.append({'price': i.text.replace("\n", "").strip().split('   ')[0],
                      'author': j.findChildren("a")[0].text.replace("\n", "").strip().split(', ')
                         , 'title': k.findChildren("span")[0].text.strip(),
                      'link': f"https://znanje.hr/{k.findChildren('a')[0]['href']}",
                      'page': 2})
    return lista
