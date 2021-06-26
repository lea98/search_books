from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import  os

# --| Setup


def knjiga(task_cont, task_title):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36")
    #driver_path = r"C:\Users\LeaBratić\Desktop\chromedriver.exe"
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=options)
    browser.minimize_window()
    # --| Parse or automation
    if task_cont and task_title:
        to_url = (task_cont + ' ' + task_title).replace(' ', '+')
    elif task_cont:
        to_url = task_cont.replace(' ', '+')
    else:
        to_url = task_title.replace(' ', '+')
    url = f"https://knjiga.hr/?s={to_url}&post_type=product"
    browser.get(url)
    browser.implicitly_wait(5)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    price = soup.findAll('span', attrs={'class','woocommerce-Price-amount amount'})
    title_meta = soup.findAll('h2', attrs={'class','woocommerce-loop-product__title'})
    authors_meta = soup.findAll('div', attrs={'class','author'})

    links=soup.findAll('div', attrs={'class','author-and-title-wrapper'})

    lista=[]

    for (i,j,k, s) in zip(price,authors_meta, title_meta, links):
        lista.append({'price':i.findChildren("bdi")[0].text.replace(u'\xa0', u' ').strip().split('   ')[0],
                      'author':j.text.replace("\n","").strip().split(', '),
                      'title':' '.join((k.text.replace("\n","").strip()).split()),
                      'link': s.findChildren('a')[0]['href'],
                      'page': 5})
    browser.quit()
    return lista