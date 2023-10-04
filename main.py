import logging
import re
import sys
import time
from logging.handlers import RotatingFileHandler
import fire
import discord

import LTE

# Logging
logger = logging.getLogger("puklaguma")
log_filename = f"logs/{time.strftime('%Y-%m-%d_%H-%M')}.log"
log_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s"
)
handler = RotatingFileHandler(log_filename, maxBytes=10 * 1024 * 1024, backupCount=5)
handler.setFormatter(log_formatter)
handler.setLevel(logging.DEBUG)

logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

LTE.logger.addHandler(handler)
LTE.logger.addHandler(logging.StreamHandler())
LTE.logger.setLevel(logging.DEBUG)

# Discord client
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# Test SMS
ADMIN_NUMBER = None
try:
    with open("admin_number.env") as file:
        ADMIN_NUMBER = file.read().strip()
except FileNotFoundError:
    logger.warning("admin_number.env not found. Test SMS will not be sent.")
WELCOME_MESSAGE = "It's time for a pit stop, Pukla guma reporting for duty!"

MAGIC_PREFIX = "$"


def get_phone_number(message):
    """Parse channel name as a phone number.

    Return None if invalid channel name.
    """

    name = message.channel.name
    name = re.sub(r"\D", "", name)[:13]

    if not re.match(r"^00386\d{8}$", name):
        return None

    return name


def get_content(message):
    """Validate message content.

    Limit content to 160 (or 70) characters and strip leading MAGIC_PREFIX.
    Return None if invalid.
    """
    content = message.content
    if not content.startswith(MAGIC_PREFIX):
        return None
    content = content[len(MAGIC_PREFIX):]

    ascii_only = re.sub(r"[^\x00-\x7F]+", "", content)
    limit = 160
    if ascii_only != content:
        limit = 70

    if len(content) > limit:
        return None
    return content


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    # Do not respond to own messages
    if message.author == client.user:
        return
    logger.info(f"Received '{message.content}' in '{message.channel.name}'")

    is_channel = isinstance(message.channel, discord.channel.TextChannel)
    if not is_channel:
        logger.info("Ignoring message in thread")
        return

    number = get_phone_number(message)
    if number is None:
        logger.info(
            f"Recipient '{message.channel.name}' (parsed '{number}') is not a valid phone number."
        )
        return

    content = get_content(message)
    if content is None:
        logger.warning("Invalid message content")
        await message.channel.send(
            f"Messages in SMS channels must start with '{MAGIC_PREFIX}' and be at most 160 characters long (70 if non-ascii)."
        )
        return

    try:
        LTE.send_sms(number, content)
        await message.channel.send(f"Sent '{content}' to {number}")
        logger.info(f"Sent '{content}' to {number}")
    except Exception as e:
        await message.channel.send(f"Failed to send '{content}' to {number}: {e}")
        logger.error(f"Failed to send SMS: {e}")


class Bot:
    def on(self):
        """Turn on LTE module."""
        LTE.power_on()

    def unlock(self, pin):
        """Unlock SIM card."""
        LTE.unlock_pin(pin)

    def off(self):
        """Turn off LTE module."""
        LTE.power_off()

    def check(self):
        """Run a health check on the LTE module."""
        LTE.health_check()
    
    def test(self, message=WELCOME_MESSAGE, recipient=ADMIN_NUMBER):
        """Send a test SMS to the admin number."""
        logger.info(f"Sending test SMS '{message}' to {recipient}")
        LTE.send_sms(recipient, message)
    
    def at(self, command):
        """Send an AT command to the LTE module."""
        logger.info(f"Sending AT command '{command}'")
        LTE.send_at(command, "OK", 10)

    def run(self):
        """Run the Discord bot."""
        LTE.health_check()
        if ADMIN_NUMBER is not None:
            self.test()

        with open("token.env") as file:
            logger.info("Starting Discord client")
            client.run(file.read())


if __name__ == "__main__":
    fire.Fire(Bot)

