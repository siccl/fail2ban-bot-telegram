#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Telegram Bot to help Fail2Ban LifeSaving.

Based on the python-telegram-bot examples.
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Using .env-sample as a template, create a .env file with your own values.
We recommend using a screen session to run the bot in the background.
Run on user with sudo privileges.

Run the bot with:
python fail2ban-bot.py
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import subprocess
from decouple import config
# Telegram Bot Authorization Token
TOKEN = config('TOKEN')
# Telegram Bot Authorized Users (Telegram User ID)
AUTORIZED_USERS = config('AUTORIZED_USERS')
import ipaddress
def validate_ip_address(ip_string):
   try:
       ip_object = ipaddress.ip_address(ip_string)
       return True
   except ValueError:
       return False

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    if user_id in AUTORIZED_USERS:
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )
    else:
        await update.message.reply_text("You are not authorized to use this bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    if user_id in AUTORIZED_USERS:
        help_text = "This bot is used to unban IP from Fail2Ban. \n\n"
        help_text += "Commands: \n"
        help_text += "/start - Start the bot \n"
        help_text += "/help - Show this help message \n"
        help_text += "/unban IP - Unban IP \n"
        help_text += "/banned - Show banned IPs by Jail \n"
        await update.message.reply_text(help_text)
    else:
        await update.message.reply_text("You are not authorized to use this bot")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text + " is not a valid command, use /help to see the valid commands")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unban IP replayed."""
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    if user_id in AUTORIZED_USERS:
        # Get IP from message
        try:
            IP = context.args[0]
        except IndexError:
            await update.message.reply_text("Please, specify an IP" + user_id)
            return
        # Check if IP is valid
        if validate_ip_address(IP):
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "Unbanning : " + IP)
            # Unban IP
            output = subprocess.check_output("sudo fail2ban-client unban " + IP, shell=True)
            if (output.decode('utf-8')=="0"):
                await context.bot.send_message(chat_id=update.effective_chat.id, text = "IP has not banned")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text = "IP has unbanned")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "Invalid IP")
    else:
        await update.message.reply_text("You are not authorized to use this bot")

async def banned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    if user_id in AUTORIZED_USERS:
        # check fail2ban version
        output = subprocess.check_output("fail2ban-client -V", shell=True)
        if (output.decode('utf-8').split(".")[0]=="0"):
            # Get all jails and banned IPs jail by jail
            output = subprocess.check_output("sudo fail2ban-client status", shell=True)
            text_var = output.decode('utf-8')
            subline = text_var.split('\n', 1)[1]
            line = subline.split('`',1)[1]
            text = line.split(':',1)[1]
            lista = text.split(',')
            for i in lista:
                output = subprocess.check_output("sudo fail2ban-client status " + i, shell=True)
                text_var = output.decode('utf-8')
                subline = text_var.split('\n', 10)[8]
                line = subline.split(':',1)[1]
                if (len(line) > 1):
                    await context.bot.send_message(chat_id=update.effective_chat.id, text = i.strip() + " Banned IPs " + line + ".")
        else:
            # Get all jails and banned IPs
            output = subprocess.check_output("sudo fail2ban-client banned", shell=True)
            await context.bot.send_message(chat_id=update.effective_chat.id, text = output.decode('utf-8'))
    else:
        await update.message.reply_text("You are not authorized to use this bot")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("banned", banned))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()