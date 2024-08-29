from logger import logger
from scraper import scraper

if __name__ == "__main__":
    logger.info("Starting up scraper...")
    slack_msg = scraper()
    logger.info("Finished scraping menus.")

    logger.info("Starting up Slack bot...")
    ...
    logger.info("Done. Check the #almoco channel.")
