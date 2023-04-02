import requests
import random
import string
from bs4 import BeautifulSoup

def get_list_of_paste_ids(wanted_lang: str):
    url = "https://pastebin.com/archive/%s" % wanted_lang
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    pastes_list = []

    for paste in soup.select("table.maintable tr td:nth-of-type(1) a[href]"):
        paste_id = paste["href"].split("/")[-1]
        pastes_list.append(paste_id)

    return pastes_list

def get_random_code(wanted_lang: str):
    paste_ids = get_list_of_paste_ids(wanted_lang)

    random_url = random.choice(paste_ids)

    # Replace the URL with the raw Pastebin URL of the code you want to download
    url = 'https://pastebin.com/raw/%s' % random_url
    print(url)

    # Send a GET request to the URL to get the code
    response = requests.get(url)

    # Save the code to a file
    with open("%s.py" % random_url, "wb") as f:
        f.write(response.content)

    print(response.status_code)

get_random_code('python')