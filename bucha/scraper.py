"""
Scrape latest posts from specified restaurants.
"""

import os
import re
import warnings
from datetime import date
from pathlib import Path
from time import sleep

import requests
from config import config
from dotenv import load_dotenv
from logger import logger
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import Menu, Restaurant, load_restaurants

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
            element = WebDriverWait(self.driver, 10).until(
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
            # check if login is successful
            username = (
                WebDriverWait(self.driver, 10)
                .until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id=":Rmkql9ad5bb9l5qq9papd5aq:"]/span')
                    )
                )
                .text
            )
        except NoSuchElementException as e:
            logger.error(f"Login unsuccessful: {e}")
            return

        logger.info(f"Logged in to {username}.")
        sleep(2)

    def download_post_image(self, post: WebElement, alias: str) -> Path | None:
        """
        Downloads first image of `post` and returns its absolute local `Path`.
        """
        # Get image source
        try:
            img = post.find_element(By.XPATH, ".//img[contains(@src, 'scontent')][1]")
            src = img.get_attribute("src")
        except NoSuchElementException as e:
            logger.error(f"No image found in post from '{alias}': {e}")

        # Download the image
        response = requests.get(src, stream=True)
        if response.status_code == 200:
            path = config.imgs_dir / f"{alias.lower().replace(' ', '-')}.jpg"
            with open(path, "wb") as file:
                _ = [
                    file.write(chunk)
                    for chunk in response.iter_content(chunk_size=1024)
                    if chunk
                ]
            logger.info(f"Image-based menu downloaded successfully.")
            return Path(path).absolute()
        else:
            logger.error(f"Something went wrong when fetching {src}.")
            return None

    def get_post_text(self, post: WebElement) -> str:
        try:
            # Click "Ver mais" button on the first post to expand content
            self.click_xpath("//div[contains(text(), 'Ver mais')]")
            # post = timeline.find_element(By.XPATH, "./div[1]")
        except NoSuchElementException:
            logger.warning(
                "Could not find a <div> element containing the text 'Ver mais'."
            )
            return

        logger.info(f"Text-based menu extracted successfully.")
        return post.text

    def format_post_body_text(
        self,
        raw_text: str | None,
        pat: str = r"(.*?)(Gosto|Todas as reações)",
    ) -> Menu:
        body_text = "Failed to extract post text."
        if raw_text:
            lines = raw_text.strip().splitlines()
            match: re.Match | None = re.compile(pat, re.DOTALL).search(
                "\n".join(lines[4:])
            )
            if match:
                match_text: str = match.group(0)
                body_text = "\n".join(match_text.strip().splitlines()[:-1])
        return body_text

    def save_menu(self, msg: str) -> None:
        today: str = date.today().isoformat().replace("-", "_")
        with open(config.menus_dir / f"{today}.txt", "w+") as f:
            f.write(msg)
        logger.info(f"Today's menu saved in {config.menus_dir}/{today}.txt.")

    def find_timeline(self) -> WebElement | None:
        try:
            timeline = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-pagelet='ProfileTimeline']")
                )
            )
            return timeline
        except NoSuchElementException as e:
            logger.error(f"Could not find profile timeline: {e}")
            return None

    def is_valid_post_timestamp(post: WebElement) -> bool:
        timestamp: dict[str, int | str | None] = {"amount": None, "unit": None}
        try:
            raw_timestamp = post.find_element(
                By.XPATH,
                "//a/span[contains(text(), 'horas') or contains(text(), 'dias') or contains(text(), 'min')]",
            ).text
            timestamp = dict(zip(timestamp, raw_timestamp.split(" ")))
        except NoSuchElementException:
            logger.error(f"Could not find timestamp element.")

        if timestamp["unit"] == "dias" and timestamp["amount"] >= 1:
            return "O menu de hoje não está disponível."

    def __call__(self) -> str:
        self.login()
        menus: list[str] = []
        for restaurant in self.accounts:
            logger.info(
                f"Fetching menu for account {restaurant.account_id} aka '{restaurant.alias}'."
            )
            self.get_page(restaurant.account_id)
            timeline = self.find_timeline()
            last_post = timeline.find_element(By.XPATH, "./div[1]")
            menu = Menu(restaurant)
            if restaurant.scraping_mode == "text":
                raw_post_text = self.get_post_text(post=last_post)
                menu.body = self.format_post_body_text(raw_post_text)
            elif restaurant.scraping_mode == "image":
                menu.img_path = self.download_post_image(last_post, restaurant.alias)
            else:
                logger.warning(
                    f"Invalid mode for account '{restaurant.account_id}'. Use either 'image' or 'text'."
                )
                continue
            menus.append(str(menu))

        msg = "\n".join(menus)

        # TODO: The following method should create a new pdf
        # with the extracted text + the images, labeled with their respective restaurant
        self.save_menu(msg)
        return msg


if __name__ == "__main__":
    logger.info("Starting up scraper...")
    restaurants = load_restaurants()
    msg = Scraper(
        accounts=restaurants,
        base_url="https://www.facebook.com/",
    )()
    logger.info("Done.")
