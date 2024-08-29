"""
Scrape latest posts from specified restaurants.
"""

import os
import re
import warnings
from datetime import date
from time import sleep
from typing import Callable

import fpdf
from config import config
from dotenv import load_dotenv
from logger import logger
from pyshorteners import Shortener
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
    pdf_writer: fpdf.FPDF

    def __init__(
        self,
        accounts: list[str],
        base_url: str,
    ) -> None:
        self.driver = self.create_driver()
        self.webdriver_wait = WebDriverWait(
            self.driver, config.default_driver_wait_timeout
        )
        self.url_shortener = Shortener()
        self.accounts = accounts
        self.base_url = base_url
        self.pdf_writer = fpdf.FPDF()
        self.pdf_writer.add_font(
            "dejavu-sans", style="", fname=config.assets_dir / "dejavu_sans.ttf"
        )

    def create_driver(self) -> WebDriver:
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        return webdriver.Firefox(options=options)

    def get_page(self, account_id: str) -> None:
        page: str = self.base_url + account_id
        try:
            self.driver.get(page)
        except Exception as e:
            logger.error(f"Couldn't fetch requested web page: {page}")
            raise e

    def click_xpath(self, expected_condition: Callable) -> None:
        try:
            element: WebElement = WebDriverWait(
                self.driver, config.default_driver_wait_timeout
            ).until(expected_condition)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        except NoSuchElementException as e:
            logger.error(f"Unable to locate element: {e}")
            return None

        try:
            element.click()
        except ElementClickInterceptedException:
            logger.warning(
                "Unable to use <element>.click() method. Trying JavaScript-based approach."
            )
            self.driver.execute_script("arguments[0].click();", element)

    def send_keys_xpath(self, xpath: str, keys: str) -> None:
        try:
            # find element
            element = WebDriverWait(
                self.driver, config.default_driver_wait_timeout
            ).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except NoSuchElementException as e:
            logger.error(f"Unable to locate element: {e}")
            return

        element.send_keys(keys)

    def login(self) -> None:
        self.get_page("")

        # handle cookie modal
        cookie_accept_xpath = "/html/body/div[3]/div[2]/div/div/div/div/div[3]/div[2]/div/div[2]/div[1]/div"
        self.click_xpath(EC.element_to_be_clickable((By.XPATH, cookie_accept_xpath)))

        # set login form fields
        self.send_keys_xpath('//*[@id="email"]', self.credentials["email"])
        self.send_keys_xpath('//*[@id="pass"]', self.credentials["password"])

        self.webdriver_wait.until(
            EC.element_to_be_clickable((By.NAME, "login"))
        ).click()

        try:
            # check if login is successful
            username = self.webdriver_wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id=":Rmkql9ad5bb9l5qq9papd5aq:"]/span')
                )
            ).text
        except NoSuchElementException as e:
            logger.error(f"Login unsuccessful: {e}")
            return

        logger.info(f"Logged in to {username}.")

    def get_img_src(self, post: WebElement, alias: str) -> str | None:
        """
        Downloads first image of `post` and returns its absolute local `Path`.
        """
        # Get image source
        try:
            img = self.webdriver_wait.until(
                lambda _: post.find_element(
                    By.XPATH, ".//img[contains(@src, 'scontent')][1]"
                )
            )
            src = img.get_attribute("src")
        except NoSuchElementException as e:
            logger.error(f"No image found in post from '{alias}': {e}")
            return None
        return self.url_shortener.tinyurl.short(src)

    def find_last_post(self, timeline: WebElement) -> WebElement:
        last_post = timeline.find_element(By.XPATH, "./div[1]")
        logger.debug(f"last_post.text: {last_post.text}")
        return last_post

    def get_post_text(self, post: WebElement) -> str:
        # Expand post content
        try:
            self.click_xpath(
                lambda _: post.find_element(
                    By.XPATH, "//div[contains(text(), 'Ver mais')]"
                )
            )
        except NoSuchElementException:
            logger.error("Could not find 'Ver mais' button in post.")

        if not post.text or len(post.text) < 10:
            logger.error("Failed to extract post text.")
            return "Failed to extract post text."

        logger.debug(post.text)
        logger.info("Text-based menu extracted successfully.")
        return post.text

    def format_post_body_text(
        self,
        raw_text: str | None,
        pat: str = r"(.*?)(Gosto|Todas as reações)",
    ) -> str:
        body_text = ""
        if raw_text:
            lines = raw_text.strip().splitlines()
            match: re.Match | None = re.compile(pat, re.DOTALL).search(
                "\n".join(lines[4:])
            )
            if match:
                match_text: str = match.group(0)
                body_text = "\n".join(match_text.strip().splitlines()[:-1])
                return body_text
            logger.warning("No matches found in the raw post text.")
        logger.warning("Failed to format post body text.")
        return body_text

    def save_menu(self, msg: str) -> None:
        today: str = date.today().isoformat().replace("-", "_")
        with open(config.menus_dir / f"{today}.txt", "w+") as f:
            f.write(msg)
        logger.info(f"Today's menu saved in {config.menus_dir}/{today}.txt.")

    def find_timeline(self) -> WebElement | None:
        try:
            timeline = WebDriverWait(
                self.driver, config.default_driver_wait_timeout
            ).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-pagelet='ProfileTimeline']")
                )
            )
            return timeline
        except NoSuchElementException as e:
            logger.error(f"Could not find profile timeline: {e}")
            return None

    def is_restaurant_closed(self) -> bool:
        try:
            raw_timestamp: WebElement = WebDriverWait(
                self.driver, config.default_driver_wait_timeout
            ).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//a/span[contains(., 'horas') or contains(., 'dias') or contains(., 'min') or (contains(., 'de') and contains(., 'às'))]",
                    )
                )
            )
            timestamp_parts = raw_timestamp.text.split(" ")
            if (
                len(timestamp_parts) > 2
                or int(timestamp_parts[0]) >= 1
                and timestamp_parts[1] == "dias"
            ):
                return True
            return False
        except NoSuchElementException:
            logger.error(f"Could not find timestamp element.")

    def __call__(self) -> str:
        self.login()
        menus: list[Menu] = []
        for restaurant in self.accounts:
            logger.info(
                f"Fetching menu for account '{restaurant.account_id}' aka '{restaurant.alias}'."
            )
            self.get_page(restaurant.account_id)
            timeline = self.find_timeline()
            last_post = self.find_last_post(timeline)
            menu = Menu(restaurant)
            if not self.is_restaurant_closed():
                if restaurant.scraping_mode == "text":
                    raw_post_text = self.get_post_text(post=last_post)
                    menu.body = self.format_post_body_text(raw_post_text)
                elif restaurant.scraping_mode == "image":
                    menu.img_path = self.get_img_src(
                        last_post,
                        restaurant.alias,
                    )
                else:
                    logger.warning(
                        f"Invalid mode for account '{restaurant.account_id}'. Use either 'image' or 'text'."
                    )
                    continue
            else:
                logger.warning(f"Restaurant is closed.")
                menu.body = "Fechado (ou ainda não publicou o menu de hoje)."
            menus.append(str(menu))

        msg = "\n".join(menus)
        self.save_menu(msg)
        return msg


scraper = Scraper(accounts=load_restaurants(), base_url="https://www.facebook.com/")
