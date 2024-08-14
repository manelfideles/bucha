# Bucha-Bot

Bucha-Bot is a Slack bot designed to streamline the lunch decision-making process for RedLight's team. It automates the collection of daily menus from selected restaurants and facilitates a quick voting session to determine the team's lunch preference.

## Features

### Menu Scraping
- Automatically scrapes lunch menus from selected restaurants' Facebook pages
- Runs daily at 11:55 AM to ensure up-to-date information

### Slack Integration
- Posts scraped menus to a dedicated channel on RedLight's Slack server
- Creates and manages a daily lunch poll

### Automated Polling
- Initiates a poll at 12:01 PM each workday
- Each restaurant is presented as a voting option
- Automatically closes the poll at 12:15 PM

## How It Works

1. **Menu Scraping (11:55 AM):**
   - The bot scrapes the day's menus from predetermined Facebook pages
   - Prepares the menu information for posting

2. **Menu Posting (12:00 PM):**
   - Posts the scraped menus to the designated Slack channel

3. **Poll Creation (12:01 PM):**
   - Creates a new poll in the Slack channel
   - Each restaurant is listed as a voting option

4. **Voting Period (12:01 PM - 12:15 PM):**
   - Team members can vote for their preferred lunch option

5. **Poll Closure (12:15 PM):**
   - The bot automatically closes the poll
   - Results are displayed in the Slack channel

## Setup and Configuration

Setup the Facebook credentials to login into Facebook in the .env file. A .env-example file is provided so you know what fields the .env file you create should contain.

## Usage

The bot has no commands for now, it's scheduled to run automatically w/ a cronjob.

## Maintenance

N/A