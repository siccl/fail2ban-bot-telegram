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

Find out your user ID by sending a message to the bot and accessing the address, with the bot token:
https://api.telegram.org/bot0000000000:00000000000000000000000000000000000/getUpdates

Usage:
    Edit the .env file with your own values.
    We recommend using a screen session to run the bot in the background.
    Run on user with sudo privileges.

Example variables for .env file:
    TOKEN=0000000000:00000000000000000000000000000000000
    AUTORIZED_USERS=000000000

You can set your default jail to block IPs:
    DEFAULT_BAN_JAIL=manual_ban


Run the bot with:
    python fail2ban-bot.py


- press Ctrl-C on the command line or send a signal to the process to stop the bot

"""

import logging
import subprocess
from decouple import config
import ipaddress

from telegram import __version__ as TG_VER
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# variables
TOKEN = config('TOKEN', default='', cast=str)
AUTORIZED_USERS = config('AUTORIZED_USERS', default='', cast=str)
DEFAULT_BAN_JAIL = config('DEFAULT_BAN_JAIL', default='', cast=str)



def validate_ip_address(ip_string):
   try:
       ip_object = ipaddress.ip_address(ip_string)
       return True
   except ValueError:
       return False

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
    user = update.effective_user
    if user_id in AUTORIZED_USERS:
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}! Send /help to see available commands.",
            reply_markup=ForceReply(selective=True),
        )
    else:
        await update.message.reply_html(f"You are not authorized to use this bot, {user.mention_html()}! ")




async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    user = update.effective_user

    if user_id in AUTORIZED_USERS:
        help_text = "This bot is used to BAN or UNban IP from Fail2Ban. \n\n"
        help_text += "Commands: \n"
        help_text += "/start => Start the bot \n"
        help_text += "/help => Show this help message \n"
        help_text += "/ban IP JAIL => BAN IP \n"
        help_text += "/unban IP => Unban IP \n"
        help_text += "/reload JAIL => Reload jail and unban all your IP addresses \n"
        help_text += "/banned => Show banned IPs by Jail \n"
        help_text += "/start_jail => Start a specific jail \n"
        help_text += "/stop_jail => Stop a specific jail \n"
        await update.message.reply_text(help_text)
    else:
        await update.message.reply_html(f"You are not authorized to use this bot, {user.mention_html()}! ")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text + " is not a valid command, use /help to see the valid commands")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    user = update.effective_user

    if user_id in AUTORIZED_USERS:
        # Get IP from message
        try:
            IP = context.args[0]
        except IndexError:
            await update.message.reply_text("Please, specify an IP ")
            return
        ###
        try:
            JAIL = context.args[1]
        except IndexError:
            await update.message.reply_text("Please, specify an Jail for the BAN \nIf you want to use the default jail '" + DEFAULT_BAN_JAIL + "', send:")
            await update.message.reply_text("/ban " + IP + " " + DEFAULT_BAN_JAIL)
            return

        # Check if IP is valid
        if validate_ip_address(IP):
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "BAN : " + IP)
            # Unban IP
            output = subprocess.check_output("sudo fail2ban-client set " + JAIL + " banip " + IP, shell=True)
            if (output.decode('utf-8')=="0"):
                await context.bot.send_message(chat_id=update.effective_chat.id, text = "=> IP has not banned")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text = "=> IP has banned")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "Invalid IP")
    else:
        await update.message.reply_html(f"You are not authorized to use this bot, {user.mention_html()}! ")


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    user = update.effective_user

    if user_id in AUTORIZED_USERS:
        # Get IP from message
        try:
            IP = context.args[0]
        except IndexError:
            await update.message.reply_text("Please, specify an IP ")
            return
        # Check if IP is valid
        if validate_ip_address(IP):
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "Unbanning : " + IP)
            # Unban IP
            output = subprocess.check_output("sudo fail2ban-client unban " + IP, shell=True)
            if (output.decode('utf-8')=="0"):
                await context.bot.send_message(chat_id=update.effective_chat.id, text = "=> IP has not banned")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text = "=> IP has unbanned")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "Invalid IP")
    else:
        await update.message.reply_html(f"You are not authorized to use this bot, {user.mention_html()}! ")

async def reload_jail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    user = update.effective_user

    if user_id in AUTORIZED_USERS:
        # Get IP from message
        try:
            JAIL = context.args[0]
        except IndexError:
            await update.message.reply_text("Please, specify an jail or use the default: '" + DEFAULT_BAN_JAIL + "'")
            return
        ###
        try:
            CONFIRM = context.args[1]
        except IndexError:
            await update.message.reply_text("*ATTENTION*: this action will reset the jail and remove all IPs from it. \nTo continue, send: \n\n/reload " + JAIL + " continue")
            return
        if CONFIRM == "continue":
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "Reloading jail : " + JAIL)
            # Unban IP
            output = subprocess.check_output("sudo fail2ban-client reload --unban " + JAIL, shell=True)
            if (output.decode('utf-8')=="0"):
                await context.bot.send_message(chat_id=update.effective_chat.id, text = "=> Jail not reloaded")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text = "=> Jail reloaded")
        else:
            await update.message.reply_text("*ATTENTION*: this action will reset the jail and remove all IPs from it. \nTo continue, send: \n\n/reload " + JAIL + " continue")
            return
    else:
        await update.message.reply_html(f"You are not authorized to use this bot, {user.mention_html()}! ")


async def banned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: ## 9500 character limit per message
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    user = update.effective_user

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
                line = line.strip()
                if (len(line) > 1):
                    line = line.replace(" ", ", ")
                    await context.bot.send_message(chat_id=update.effective_chat.id, text = i.strip() + " banned IPs: " + line)
                # else: await context.bot.send_message(chat_id=update.effective_chat.id, text = "There is currently no IP in the jail " + i.strip())
        else:
            # Get all jails and banned IPs
            output = subprocess.check_output("sudo fail2ban-client banned", shell=True)
            await context.bot.send_message(chat_id=update.effective_chat.id, text = output.decode('utf-8'))
    else:
        await update.message.reply_html(f"You are not authorized to use this bot, {user.mention_html()}! ")


async def start_jail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    user = update.effective_user

    if user_id in AUTORIZED_USERS:
        # Get IP from message
        try:
            JAIL = context.args[0]
        except IndexError:
            await update.message.reply_text("Please, specify an jail or use the default: " + DEFAULT_BAN_JAIL)
            return
        await context.bot.send_message(chat_id=update.effective_chat.id, text = "Starting Jail : " + JAIL)
        # Unban IP
        output = subprocess.check_output("sudo fail2ban-client start " + JAIL, shell=True)
        output_service = subprocess.check_output("sudo /etc/init.d/fail2ban restart ", shell=True)
        if (output.decode('utf-8')=="0"):
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "=> Jail not started")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "=> Jail started")

    else:
        await update.message.reply_html(f"You are not authorized to use this bot, {user.mention_html()}! ")


async def stop_jail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check if user is authorized
    user_id = str(update.effective_user.id)
    user = update.effective_user

    if user_id in AUTORIZED_USERS:
        # Get IP from message
        try:
            JAIL = context.args[0]
        except IndexError:
            await update.message.reply_text("Please, specify an jail or use the default: " + DEFAULT_BAN_JAIL)
            return
        await context.bot.send_message(chat_id=update.effective_chat.id, text = "Stopping jail : " + JAIL)
        # Unban IP
        output = subprocess.check_output("sudo fail2ban-client start " + JAIL, shell=True)
        output_service = subprocess.check_output("sudo /etc/init.d/fail2ban restart ", shell=True)
        if (output.decode('utf-8')=="0"):
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "=> Jail not stopped")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text = "=> Jail stopped")

    else:
        await update.message.reply_html(f"You are not authorized to use this bot, {user.mention_html()}! ")






def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("reload", reload_jail))
    application.add_handler(CommandHandler("banned", banned))
    application.add_handler(CommandHandler("start_jail", start_jail))
    application.add_handler(CommandHandler("stop_jail", stop_jail))


    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
