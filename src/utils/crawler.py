import requests
import random
import string

while True:
    # Replace the URL with the raw Pastebin URL of the code you want to download
    url = "https://pastebin.com/raw/%s" % (''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=8)))
    # url = 'https://pastebin.com/raw/Pj04irL5' # Test URL, which should exist and be properly downloaded
    print(url)

    # Send a GET request to the URL to get the code
    response = requests.get(url)

    # Save the code to a file
    with open("code.py", "w") as f:
        f.write(response.text)

    print(response.status_code)
    if response.status_code != 404:
        break