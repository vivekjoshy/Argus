import logging
import warnings

import sentry_sdk
from odmantic import AIOEngine
from sentry_sdk.integrations.logging import (
    BreadcrumbHandler,
    EventHandler,
    LoggingIntegration,
)

from argus.client import ArgusClient
from argus.config import config
from argus.db.mongo import MongoClient
from argus.logger import logger

# Logging Config
environment = "production" if config["bot"]["production"] else "development"
sentry_sdk.init(
    config["logs"]["sentry"],
    environment=environment,
    integrations=[LoggingIntegration(level=None, event_level=None)],
    traces_sample_rate=1.0,
)
logger.add(BreadcrumbHandler(level=logging.DEBUG), level=logging.DEBUG)
logger.add(EventHandler(level=logging.ERROR), level=logging.ERROR)

if environment == "production":
    logger.add(
        ".logs/{time}_discord.log",
        rotation="50 MB",
        retention="15 days",
        filter="discord",
        level=logging.DEBUG,
    )
    logger.add(
        ".logs/{time}_general.log",
        rotation="50 MB",
        retention="15 days",
        filter="argus",
        level=logging.INFO,
    )
else:
    logger.add(
        ".logs/{time}_discord.log",
        rotation="10 MB",
        retention="2 days",
        filter="discord",
        level=logging.DEBUG,
    )
    logger.add(
        ".logs/{time}_general.log",
        rotation="10 MB",
        retention="2 days",
        filter="argus",
        level=logging.INFO,
    )


def showwarning(message, category, filename, lineno, file=None, line=None):
    new_message = warnings.formatwarning(message, category, filename, lineno, line)
    logger.warning(new_message)


warnings.showwarning = showwarning

# Setup Database
db = MongoClient(config=config)
engine = AIOEngine(client=db, database=config["database"]["name"])

# Initialize Bot
bot = ArgusClient(config, logger)
bot.remove_command("help")

with open("resources/propositions.txt") as p:
    propositions = p.readlines()

bot.state["propositions"] = propositions
