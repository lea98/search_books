from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.wait import WebDriverWait


def get_currency(product):
    try:
        product.find_element_by_xpath(".//p[@class='price']//ins/span")
        return product.find_element_by_xpath(
            ".//p[@class='price']//ins/span"
        ).text.replace("\xa0", " ")

    except NoSuchElementException:
        return product.find_element_by_xpath(".//p[@class='price']/span").text.replace(
            "\xa0", " "
        )


def get_authors(product, index):
    list_au = []
    auth = product.find_elements_by_xpath(
        f"(//div[@class='books-container']/div[contains(@class,'book')])[{index}]//div[@class='author']//a"
    )
    for au in auth:
        list_au.append(au.text)

    return list_au


def form_text_to_send(task_title, task_cont):
    if task_title and task_cont:
        text_to_send = task_cont + " " + task_title + Keys.ENTER
    elif task_title:
        text_to_send = task_title + Keys.ENTER
    elif task_cont:
        text_to_send = task_cont + Keys.ENTER
    else:
        return []

    return text_to_send


def mozaik(auth_name, book_title):
    options = Options()
    options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    )
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    # LOCAL TESTING - change executeble path
    # driver_path = r"C:\Users\LeaBratić\Desktop\chromedriver.exe"

    driver = webdriver.Chrome(
        executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options
    )
    driver.minimize_window()
    # --| Parse or automation
    url = "https://mozaik-knjiga.hr/"
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@class='pretrazi-knjige']"))
    )

    text_to_send = form_text_to_send(auth_name, book_title)

    input_element = driver.find_element_by_xpath("//input[@class='pretrazi-knjige']")
    input_element.send_keys(text_to_send)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h1[contains(text(),'Rezultati')]"))
    )

    try:
        all_books = driver.find_elements_by_xpath(
            "//div[@class='books-container']/div[contains(@class,'book')]"
        )
    except NoSuchElementException:
        return []

    lista = []
    for index, one_book in enumerate(all_books):
        lista.append(
            {
                "price": get_currency(one_book),
                "author": get_authors(one_book, index + 1),
                "title": one_book.find_element_by_xpath(
                    ".//div[@class='title']//a"
                ).get_attribute("title"),
                "link": one_book.find_element_by_xpath(
                    ".//div[@class='title']//a"
                ).get_attribute("href"),
                "page": 3,
            }
        )

    driver.quit()
    return lista
