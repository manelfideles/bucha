#!/bin/bash

# Load incoming webhook URL
export $(xargs < .env)

poetry run python bucha/main.py

latest_menu_filename=$(ls -t out/menus | head -n1)
latest_menu=$(cat "out/menus/$latest_menu_filename")

curl -H 'Content-Type: application/json' \
     -d "{\"text\": \"$latest_menu\", "unfurl_links": false, "unfurl_media": false }" \
     -X POST \
     "$SLACK_INCOMING_WEBHOOK_URL_DEV"