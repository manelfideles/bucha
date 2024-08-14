"""
Scrape latest posts from specified restaurants.
For now, only text-based posts are supported.
"""

import argparse
import os
import re
import warnings
from datetime import date
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Setup ----
for w in [SyntaxWarning, UserWarning]:
    warnings.filterwarnings(action="ignore", category=w)

load_dotenv()

CREDENTIALS = {
    "email": os.environ.get("FACEBOOK_USERNAME"),
    "password": os.environ.get("FACEBOOK_PASSWORD"),
}


class Scraper:
    """
    Scrapes Facebook for the last post of the `account_ids` defined.
    Returns the Slack message containing the all the menus.
    """

    driver: WebDriver
    credentials: dict[str, str] = CREDENTIALS
    account_ids: list[str]
    base_url: str

    def __init__(
        self,
        account_ids: list[str],
        base_url: str,
    ) -> None:
        self.driver = self.create_driver()
        self.account_ids = account_ids
        self.base_url = base_url

    def create_driver(self) -> WebDriver:
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        return webdriver.Firefox(options=options)

    def get_page(self, account_id: str) -> None:
        self.driver.get(self.base_url + account_id)
        sleep(2)

    def click_xpath(self, xpath: str) -> None:
        try:
            # find element
            element = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            # scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        except NoSuchElementException as e:
            print(f"Unable to locate element: {e}")
            return

        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)
        sleep(1)

    def send_keys_xpath(self, xpath: str, keys: str) -> None:
        try:
            # find element
            element = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        except NoSuchElementException as e:
            print(f"Unable to locate element: {e}")
            return

        element.send_keys(keys)
        sleep(2)

    def login(self) -> None:
        self.get_page("")

        # handle cookie modal
        self.click_xpath(
            "/html/body/div[3]/div[2]/div/div/div/div/div[3]/div[2]/div/div[2]/div[1]/div"
        )

        # set login form fields
        self.send_keys_xpath('//*[@id="email"]', self.credentials["email"])
        self.send_keys_xpath('//*[@id="pass"]', self.credentials["password"])

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "login"))
        ).click()

        sleep(2)

    def get_last_post_text(self) -> str:
        account_feed = self.driver.find_element(
            By.XPATH, "//div[@data-pagelet='ProfileTimeline']"
        )

        # Click "Ver mais" button on the first post to expand content
        try:
            self.click_xpath("//div[contains(text(), 'Ver mais')]")
        except Exception as e:
            print(e)

        last_post = account_feed.find_element(By.XPATH, "./div[1]")

        if last_post:
            return last_post.text
        return None

    def format_post_text(
        self, raw_text: str | None, account_id: str, pat: str
    ) -> dict[str, str] | None:
        menu_info: dict[str, str] = {
            "id": account_id,
            "name": "",
            "body": "",
        }

        if raw_text:
            lines = raw_text.strip().splitlines()
            restaurant_name = lines[0]
            body_text = "\n".join(lines[3:])
            match: re.Match = re.compile(pat, re.DOTALL).search(body_text)
            if match:
                matched_text: str = match.group(0)
                formatted_body: str = (
                    "\n".join(matched_text.strip().splitlines()[:-1]) if match else ""
                )

            menu_info["name"] = restaurant_name
            menu_info["body"] = formatted_body

        sep: str = "*" * 15
        return f"{sep}\n{menu_info['name']}\n\n{menu_info['body']}\n{sep}"

    def __call__(self) -> str:
        self.login()
        msg = f"[{date.today().isoformat()}] MENUS:\n"
        menus: list[str] = []
        for account_id in self.account_ids:
            self.get_page(account_id)
            raw_text = self.get_last_post_text()
            menu = self.format_post_text(
                raw_text=raw_text,
                account_id=account_id,
                pat=r"(.*?)Todas as reações",
            )
            menus.append(menu)

        return msg + "\n".join(menus)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="scraper.py",
        description="A simple Facebook scraper to fetch a given restaurant's menu",
    )
    parser.add_argument(
        "account_ids",
        help="A list of restaurant Facebook usernames",
        type=str,
    )
    args: dict[str, str] = vars(parser.parse_args())

    msg = Scraper(
        account_ids=args["account_ids"].split(),
        base_url="https://www.facebook.com/",
    )()

    print(msg)
