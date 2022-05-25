import asyncio
import sys

import sentry_sdk
import structlog_sentry_logger
import toml

import argus
from argus.client import ArgusClient
from argus.conifg import config_schema


def start(**kwargs):
    """
    Starts the bot and obtains all necessary config data.
    """
    # Config Loader
    try:
        config = toml.load(kwargs["config_file"])
    except FileNotFoundError:
        sys.exit()

    # Validate Config
    config_schema.validate(config)

    # Faster Event Loop
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

    # Override configs from config file with ones from cli
    if kwargs["log_level"]:
        config["bot"]["log_level"] = kwargs["log_level"].upper()

    # Logging Config
    sentry_sdk.init(config["bot"]["sentry"], traces_sample_rate=1.0)

    logger = structlog_sentry_logger.get_logger()

    # Initialize Bot
    bot = ArgusClient(config, logger)
    bot.remove_command("help")

    bot.logger.info(f"Starting Argus", version=argus.__version__)

    try:
        bot.run(config["bot"]["token"])
    except (KeyboardInterrupt, SystemExit, RuntimeError):
        bot.logger.info(f"Shutting Down Argus")
    finally:
        sys.exit()
