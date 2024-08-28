"""
Scrape latest posts from specified restaurants.
"""

import os
import re
import warnings
from datetime import date
from logging import getLogger
from time import sleep

import requests
from config import Restaurant, restaurants
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = getLogger("scraper")

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
    accounts: list[Restaurant]
    base_url: str

    def __init__(
        self,
        accounts: list[str],
        base_url: str,
    ) -> None:
        self.driver = self.create_driver()
        self.accounts = accounts
        self.base_url = base_url

    def create_driver(self) -> WebDriver:
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        return webdriver.Firefox(options=options)

    def get_page(self, account_id: str) -> None:
        page: str = self.base_url + account_id
        try:
            self.driver.get(page)
            sleep(2)
        except Exception as e:
            logger.error(f"Couldn't fetch requested web page: {page}")
            raise e

    def click_xpath(self, xpath: str) -> None:
        try:
            element = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        except NoSuchElementException as e:
            logger.error(f"Unable to locate element: {e}")
            return

        try:
            element.click()
        except ElementClickInterceptedException:
            logger.warning(
                "Unable to use <element>.click() method. Trying JavaScript-based approach."
            )
            self.driver.execute_script("arguments[0].click();", element)
        sleep(1)

    def send_keys_xpath(self, xpath: str, keys: str) -> None:
        try:
            # find element
            element = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        except NoSuchElementException as e:
            logger.error(f"Unable to locate element: {e}")
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

        try:
            # find username tag
            username = self.driver.find_element(
                By.XPATH,
                '//*[@id=":Rmkql9ad5bb9l5qq9papd5aq:"]/span',
            ).text
        except NoSuchElementException as e:
            logger.error(f"Login unsuccessful: {e}")
            return

        logger.info(f"Logged in to {username}.")
        sleep(2)

    def get_last_post_text(self, alias: str) -> str:
        account_feed = self.driver.find_element(
            By.XPATH, "//div[@data-pagelet='ProfileTimeline']"
        )

        # Click "Ver mais" button on the first post to expand content
        try:
            self.click_xpath("//div[contains(text(), 'Ver mais')]")
        except Exception as e:
            logger.error(e)

        post = account_feed.find_element(By.XPATH, "./div[1]")
        # timestamp = post.find_element(
        #     By.XPATH,
        #     "/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/div/span[1]/span/a/span",
        # ).text

        # logger.info(timestamp)

        # if "dias" not in timestamp:
        if post:
            logger.info(
                f"Text-based menu for account '{alias}' extracted successfully."
            )
            return post.text
        # logger.warning("Latest post is from yesterday or older.")
        return "O menu de hoje (ainda) não está disponível."

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
        if response.status_code == 200:
            path = os.path.join("imgs", f"{account_id}.jpg")
            with open(path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            logger.info(
                f"Image-based menu for account '{alias}' downloaded successfully."
            )
        else:
            logger.error(f"Something went wrong when fetching {src}.")

    def format_post_text(
        self,
        raw_text: str | None,
        r: Restaurant,
        pat: str = r"(.*?)(Gosto|Todas as reações)",
    ) -> dict[str, str] | None:
        display_name = f"{r.emoji} - {r.alias} [{r.daily_price} Eur]"
        menu_info: dict[str, str] = {"name": display_name, "body": ""}

        if raw_text:
            lines = raw_text.strip().splitlines()
            body_text = "\n".join(lines[3:])
            match: re.Match | None = re.compile(pat, re.DOTALL).search(body_text)
            formatted_body = ""
            if match:
                matched_text: str = match.group(0)
                formatted_body = "\n".join(matched_text.strip().splitlines()[:-1])
            else:
                logger.warning(f"Failed to extract post text for account '{r.alias}'.")
                formatted_body = "Failed to extract post text."

            menu_info["body"] = formatted_body

        return menu_info

    def format_menu_info(self, menu_info: dict[str, str]) -> str:
        return f"{menu_info['name']}\n{menu_info['body']}\n"

    def save_menu(self, msg: str) -> None:
        today: str = date.today().isoformat().replace("-", "_")
        with open(f"menus/{today}.txt", "w+") as f:
            f.write(msg)
        print(f"Today's menu saved in menus/{today}.txt.")

    def __call__(self) -> str:
        self.login()
        header = f"Ora viva camaradas! Aqui vão os menus de hoje ({date.today().isoformat()}). Bom proveito 🥘\n\n"
        menus: list[str] = []
        for restaurant in self.accounts:
            logger.info(f"Fetching menu for {restaurant.account_id}...")
            self.get_page(restaurant.account_id)
            if restaurant.scraping_mode == "text":
                raw_text = self.get_last_post_text(restaurant.alias)
                menu = self.format_post_text(raw_text=raw_text, r=restaurant)
            elif restaurant.scraping_mode == "image":
                self.get_last_post_image(
                    restaurant.account_id,
                    restaurant.alias,
                )
            else:
                logger.warning(
                    f"Invalid mode for account {restaurant.account_id}. Use either 'image' or 'text'."
                )
                continue
            if menu:
                logger.info(f"Successfully fetched {restaurant.account_id}'s menu!")
            menus.append(self.format_menu_info(menu))

        msg = header + "\n".join(menus)
        self.save_menu(msg)
        return msg


if __name__ == "__main__":
    logger.info("Starting up scraper...")
    msg = Scraper(
        accounts=restaurants,
        base_url="https://www.facebook.com/",
    )()
    logger.info("Done.")
