import asyncio
import sys

import structlog_sentry_logger
import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

import argus
from argus.app import bot, logger, db
from argus.config import config
from argus.web import api

# Create App Instance
app = FastAPI(title="Argus", version=argus.__version__)
app.add_middleware(SessionMiddleware, secret_key=config["bot"]["secret_key"])
app.include_router(api.v1.oauth_client.router)

# Faster Event Loop
try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


@app.on_event("startup")
async def startup_event():
    bot.logger.info(f"Starting Argus", version=argus.__version__)
    bot.db = db
    asyncio.create_task(bot.start(config["bot"]["token"]))
    await asyncio.sleep(4)


@app.on_event("shutdown")
async def shutdown_event():
    await bot.close()


def main():
    try:
        uvicorn.run(
            app="argus.__main__:app",
            host="127.0.0.1",
            port=5000,
            debug=config["bot"]["debug"],
            log_config=structlog_sentry_logger.get_config_dict(),
            log_level=config["bot"]["log_level"].lower(),
        )
    except (KeyboardInterrupt, SystemExit, RuntimeError):
        logger.info(f"Shutting Down Argus")
    finally:
        sys.exit()


if __name__ == "__main__":
    main()
