import sentry_sdk
import structlog_sentry_logger
from odmantic import AIOEngine

from argus.client import ArgusClient
from argus.config import config
from argus.db.mongo import MongoClient

# Logging Config
sentry_sdk.init(config["bot"]["sentry"], traces_sample_rate=1.0)
logger = structlog_sentry_logger.get_logger()

# Setup Database
db = MongoClient(config=config)
engine = AIOEngine(motor_client=db, database=config["database"]["database"])

# Initialize Bot
bot = ArgusClient(config, logger)
bot.remove_command("help")

with open("resources/propositions.txt") as p:
    propositions = p.readlines()

bot.state["propositions"] = propositions
