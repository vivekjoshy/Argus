import asyncio
import sys

import argus
from argus.app import bot, logger, db, engine
from argus.config import config

# Faster Event Loop
try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

bot.logger.info(f"Starting Argus", version=argus.__version__)
bot.db = db
bot.engine = engine


def main():
    try:
        bot.run(config["bot"]["token"], log_handler=None)
    except (KeyboardInterrupt, SystemExit, RuntimeError):
        logger.info(f"Shutting Down Argus")
    finally:
        sys.exit()


if __name__ == "__main__":
    main()
