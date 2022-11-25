import sys

import toml
from schema import Or, Schema

config_schema = Schema(
    {
        "bot": {
            "token": str,
            "debug": Or(True, False),
            "production": Or(True, False),
        },
        "logs": {
            "level": Or(
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL",
            ),
            "sentry": str,
        },
        "database": {"uri": str, "name": str},
        "global": {"name": str, "guild_id": int},
    },
    ignore_extra_keys=True,
)

# Config Loader
try:
    config = toml.load("config.toml")
except FileNotFoundError:
    sys.exit()

# Validate Config
config_schema.validate(config)
