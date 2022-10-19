# fail2ban-bot-telegram

## Telegram Bot to help Fail2Ban LifeSaving

When you have rules to block any suspicions actions and need to UnBan or check all actually banned IPs with not full server access

## Based on the python-telegram-bot examples

you can see original code on :

<https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py>


First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.

Then, the bot is started and runs until we press Ctrl-C on the command line.

## Usage

Using .env-sample as a template, create a .env file with your own values.

We recommend using a screen session to run the bot in the background.

Run on user with sudo privileges.

## Run the bot with

python fail2ban-bot.py

Press Ctrl-C on the command line or send a signal to the process to stop the bot.