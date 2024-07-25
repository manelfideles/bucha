"""
Scrape latest posts from specified restaurants.
For now, only text-based posts are supported.
"""

import argparse
import logging
import os
import warnings

from dotenv import load_dotenv
from facebook_scraper import enable_logging, get_posts, logger

# Setup ----
for w in [SyntaxWarning, UserWarning]:
    warnings.filterwarnings(action="ignore", category=w)

load_dotenv()

CREDENTIALS = (
    os.environ.get("FACEBOOK_USERNAME"),
    os.environ.get("FACEBOOK_PASSWORD"),
)


def fetch_last_post(
    username, credentials: dict[str, str] = CREDENTIALS
) -> dict[str, str] | str:
    try:
        posts = get_posts(account=username, pages=1, credentials=credentials)
        last_post = next(posts)

        text = last_post.get("text", "No text content")
        timestamp = last_post.get("time", "No timestamp available")

        return {"text": text, "time": timestamp}
    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="scraper.py",
        description="A simple Facebook scraper to fetch a given restaurant's menu",
    )
    parser.add_argument(
        "restaurant_id", help="The restaurant's Facebook username", type=str
    )
    args = vars(parser.parse_args())

    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(f"logs/{args['restaurant_id']}.txt")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    enable_logging()
    last_post = fetch_last_post(username=args["restaurant_id"])
