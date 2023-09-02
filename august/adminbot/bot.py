import os
import sys
import threading
import time

import dotenv
import requests
from playwright.sync_api import sync_playwright

from webhook_logger import WebHookLogger


dotenv.load_dotenv()

if len(sys.argv) != 3:
    HOST = "127.0.0.1"
    PORT = "1337"
else:
    HOST = sys.argv[1]
    PORT = sys.argv[2]

BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    print("Environment variable BOT_TOKEN not found! Exiting...")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if WEBHOOK_URL is None:
    print("Environment variable WEBHOOK_URL not found! Exiting...")




def get_cookie() -> str:
    """
    Get the adminbot cookie from the backdoor
    """
    r = requests.get(f"http://{HOST}:{PORT}/api/g3t_c00ki3_f0r_b0tt_asdaasd", headers={"Authorization": BOT_TOKEN})
    return r.json()["cookie"]


def check_for_new_posts() -> list[str]:
    """
    Check for new posts
    """
    r = requests.get(f"http://{HOST}:{PORT}/api/g3t_4ll_p0sts_th4t_4r3_uns33n_asdaasd", headers={"Authorization": BOT_TOKEN})
    return r.json()["unseen"]



def check_post(link):
    try:
        cookie = get_cookie()
    except Exception as e:
        wh_logger.error(f"Error getting cookie, {e}")
        print("Error getting cookie")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(
            args=[
                "--disable-web-security",
                "--ignore-certificate-errors",
                "--no-sandbox"
            ]
        )
        context = browser.new_context()
        context.add_cookies([{"name": "token", "value": cookie, "domain": HOST, "path": "/"}])
        page = context.new_page()
        try:
            page.goto(f"http://{HOST}:{PORT}/view/{link}", wait_until="networkidle")
        except Exception as e:
            wh_logger.error(f"Error viewing post {link}, {e}")
            print(e)
        else:
            print(f"Viewed {link}")

        page.close()
        context.close()
        browser.close()


def main():
    while True:
        time.sleep(10)

        try:
            posts = check_for_new_posts()
        except Exception as e:
            wh_logger.error(f"Error getting posts, {e}")
            print("Error getting posts")
            print(e)
            continue

        if not posts:
            print("No new posts found")
            continue

        for post in posts:
            print(f"Checking {post}")
            wh_logger.info(f"Checking {post}")
            threading.Thread(target=check_post, args=(post,)).start()


if __name__ == "__main__":
    wh_logger = WebHookLogger(WEBHOOK_URL, "AdminBot")
    wh_logger.start()
    main()