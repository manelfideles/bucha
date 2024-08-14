"""
Scrape latest posts from specified restaurants.
"""

import argparse
import os
import re
import warnings
from datetime import date
from time import sleep

import requests
from dotenv import load_dotenv
from PIL import Image
from pytesseract import pytesseract
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
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
    Scrapes Facebook for the last post of the `accounts` defined.
    Returns the Slack message containing the all the menus.
    """

    driver: WebDriver
    credentials: dict[str, str] = CREDENTIALS
    accounts: list[tuple[str, str]]
    base_url: str

    def __init__(
        self,
        accounts: list[str],
        base_url: str,
    ) -> None:
        self.driver = self.create_driver()
        self.accounts = [tuple(a.replace("-", " ").split(",")) for a in accounts]
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

    def get_last_post_text(self, alias: str) -> str:
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
            print(f"Text-based menu for account '{alias}' extracted successfully.")
            return last_post.text
        return None

    def get_last_post_image(self, account_id: str, alias: str) -> ...:
        account_feed = self.driver.find_element(
            By.XPATH, "//div[@data-pagelet='ProfileTimeline']"
        )

        # Get image source
        img = account_feed.find_element(
            By.XPATH, ".//img[contains(@src, 'scontent')][1]"
        )
        src = img.get_attribute("src")

        # Download the image
        response = requests.get(src, stream=True)
        path = os.path.join("imgs", f"{account_id}.jpg")
        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Image-based menu for account '{alias}' downloaded successfully.")

    def extract_text_from_image(self, image_path: str) -> str:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text

    def format_image_text(self, raw_text: str, alias: str) -> str:
        menu_info = {
            "name": alias,
            "body": (
                raw_text.strip().replace("\n\n", "\n")
                if len(raw_text) > 50
                else "Not enough text available for extraction."
            ),
        }
        return menu_info

    def format_post_text(
        self, raw_text: str | None, alias: str, pat: str
    ) -> dict[str, str] | None:
        menu_info: dict[str, str] = {
            "name": alias,
            "body": "",
        }

        if raw_text:
            lines = raw_text.strip().splitlines()
            body_text = "\n".join(lines[3:])
            match: re.Match = re.compile(pat, re.DOTALL).search(body_text)
            if match:
                matched_text: str = match.group(0)
                formatted_body: str = (
                    "\n".join(matched_text.strip().splitlines()[:-1]) if match else ""
                )
            menu_info["body"] = formatted_body

        return menu_info

    def format_menu_info(self, menu_info: dict[str, str]) -> str:
        sep: str = "-" * 20
        return f"*{menu_info['name']}*\n{sep}\n{menu_info['body']}\n"

    def save_menu(self, msg: str) -> None:
        today: str = date.today().isoformat().replace("-", "_")
        with open(f"menus/{today}.txt", "w+") as f:
            f.write(msg)
        print(f"Today's menu saved in menus/{today}.txt.")

    def __call__(self) -> str:
        self.login()
        header = f"Ora viva camaradas! Aqui vão os menus de hoje ({date.today().isoformat()}). Bom proveito 🥘\n\n"
        menus: list[str] = []
        for id, alias, mode in self.accounts:
            self.get_page(id)
            if mode == "text":
                raw_text = self.get_last_post_text(alias)
                menu = self.format_post_text(
                    raw_text=raw_text,
                    alias=alias,
                    pat=r"(.*?)Todas as reações",
                )
            elif mode == "image":
                self.get_last_post_image(id, alias)
                raw_text = self.extract_text_from_image(f"imgs/{id}.jpg")
                menu = self.format_image_text(raw_text, alias)
            else:
                print(f"Invalid mode for account {id}. Use either 'image' or 'text'.")
                continue
            menus.append(self.format_menu_info(menu))

        msg = header + "\n".join(menus)
        self.save_menu(msg)
        return msg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="scraper.py",
        description="A simple Facebook scraper to fetch a given restaurant's menu",
    )
    parser.add_argument(
        "accounts",
        help="A list of restaurant Facebook usernames",
        type=str,
    )
    args: dict[str, str] = vars(parser.parse_args())

    msg = Scraper(
        accounts=args["accounts"].split(),
        base_url="https://www.facebook.com/",
    )()
