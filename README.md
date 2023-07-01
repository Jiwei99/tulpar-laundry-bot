# Tulpar Laundry Bot
## Description
The Tulpar Laundry Bot is a Telegram Bot used to track realtime Laundry machine usage in CAPT's Tulpar House.

## Dependencies
The following Python packages are used:
* `python-telegram-bot[job-queue]`: Handling bot requests and integration with Telegram API
* `firebase-admin`: Integration of the bot with Firebase Realtime Database
* `python-dotenv`: Use of environment variables from `.env` file
* `flask`: Creating REST API endpoints for webhook

## Services
The following cloud services are used:
* `Firebase Realtime Database`: Cloud database used to persist bot data
* `Google Cloud Run`: Cloud service used to run bot's backend service serverlessly
* `Telegram BotFather`: Telegram's bot management bot used to create and set up bot

## Bot Commands

### `/start`
Starts the bot.

### `/status`
Check the usage status of each Washer and Dryer machine.

### `/use`
Use a Washer or Dryer machine.

### `/ping`
Notify the user of a Washer or Dryer that their cycle has completed.

### `/done`
Indicate that you have already removed your clothes after the machine is done.

### `/clear`
Clear your use of any machine in case of errors.

## Running on Server


## Hosting on Serverless
