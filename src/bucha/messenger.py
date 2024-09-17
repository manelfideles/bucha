import os

from logger import logger
from requests import post


def send_slack_message(msg: str) -> ...:
    webhook_url = os.environ.get("SLACK_INCOMING_WEBHOOK_URL")
    payload = {"text": msg, "unfurl_links": False, "unfurl_media": False}
    try:
        response = post(webhook_url, json=payload)
        if response.status_code == 200:
            print("Menus sent, check the #almoco channel.")
    except Exception as e:
        logger.error(f"Could not send the menu to Slack: {e}")
