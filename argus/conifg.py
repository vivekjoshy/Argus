from schema import Optional, Or, Schema

config_schema = Schema(
    {
        "bot": {
            "token": str,
            "debug": Or(True, False),
            "log_level": Or(
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL",
            ),
            "sentry": str,
        },
        "database": {
            # Schema hooks can be used to force driver detail checks
            # as noted in https://git.io/fhhd2 instead of resorting
            # to blanket optionals. Will get to this later if more
            # databases are needed!
            "enabled": Or(True, False),
            Optional("driver"): "mongo",
            Optional("uri"): str,
            Optional("host"): [str],
            Optional("port"): int,
            Optional("username"): str,
            Optional("password"): str,
            Optional("database"): str,
            Optional("replica"): str,
        },
        "global": {"name": str, "guild_id": int},
    },
    ignore_extra_keys=True,
)
