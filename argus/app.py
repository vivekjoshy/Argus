from queue import Queue

import sentry_sdk
import structlog_sentry_logger
from odmantic import AIOEngine
from slowapi import Limiter
from slowapi.util import get_remote_address

from argus.client import ArgusClient
from argus.config import config
from argus.db.mongo import MongoClient

# Logging Config
sentry_sdk.init(config["bot"]["sentry"], traces_sample_rate=1.0)
logger = structlog_sentry_logger.get_logger()

# Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["5/second"])

# Setup Database
db = MongoClient(config=config)
engine = AIOEngine(motor_client=db, database=config["database"]["database"])

# Initialize Bot
bot = ArgusClient(config, logger)
bot.remove_command("help")

with open("resources/propositions.txt") as p:
    propositions = p.readlines()

bot.state = {
    "roles_are_setup": False,
    "channels_are_setup": False,
    "map_roles": {},
    "map_channels": {},
    "debates_enabled": False,
    "debate_rooms": [],
    "interface_messages": [],
    "exiting": False,
    "debate_feed_fifo": Queue(),
    "voice_channel_update_task": None,
    "debate_feed_updater_task": None,
    "propositions": propositions,
}
