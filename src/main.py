from bucha.messenger import send_slack_message
from bucha.scraper import scraper


def handler(event, context):
    print("Buchabot is alive 🍕")
    print("Running scraper...")
    msg = scraper()
    print("Today's menu " + 5 * "-")
    print(msg)
    send_slack_message(msg)
    print("Done.")
