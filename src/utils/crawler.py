import requests
import random
import os
from bs4 import BeautifulSoup

langs_and_extensions = {'python' : 'py', 'cpp' : 'cpp', 'c' : 'c', 'php' : 'php', 'c++' : 'cpp', 'py' : 'py', 'java' : 'java'}
langs_and_archives = {'python' : 'python', 'cpp' : 'cpp', 'c' : 'c', 'php' : 'php', 'c++' : 'cpp', 'py' : 'python', 'java' : 'java'}

def get_list_of_paste_ids(wanted_lang: str):
    url = "https://pastebin.com/archive/%s" % langs_and_archives[wanted_lang]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    pastes_list = []

    for paste in soup.select("table.maintable tr td:nth-of-type(1) a[href]"):
        paste_id = paste["href"].split("/")[-1]
        pastes_list.append(paste_id)

    return pastes_list

# Returns file's relative directory
def get_random_code(wanted_lang: str):
    paste_ids = get_list_of_paste_ids(wanted_lang)

    random_url = random.choice(paste_ids)

    # Replace the URL with the raw Pastebin URL of the code you want to download
    url = 'https://pastebin.com/raw/%s' % random_url

    # Create the directory for file, if it does not exist
    dir = "code_base/%s" % langs_and_archives[wanted_lang]
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Send a GET request to the URL to get the code
    response = requests.get(url)

    # Make name of file's relative directory
    file_path = "code_base/%s/%s.%s" % (langs_and_archives[wanted_lang], random_url, langs_and_extensions[wanted_lang])

    # Save the code to a file
    with open(file_path, "wb") as f:
        f.write(response.content)

    return file_path