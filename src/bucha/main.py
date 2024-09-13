from scraper import scraper

if __name__ == "__main__":
    print("Starting up scraper...")
    slack_msg = scraper()
    print("Finished scraping menus.")

    print("Starting up Slack bot...")
    ...
    print("Done. Check the #almoco channel.")
