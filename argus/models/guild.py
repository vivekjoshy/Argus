from typing import Dict, Optional

from odmantic import Model, Field

from argus.models import DiscordGuild, DiscordRole, DiscordChannel


class GuildModel(Model):
    guild: DiscordGuild = Field()
    roles: Optional[Dict[str, DiscordRole]] = Field()
    channels: Optional[Dict[str, DiscordChannel]] = Field()

    # Schema
    class Config:
        schema_extra: dict = {
            "examples": [
                {
                    "guild": 769148380156133416,
                    "roles": [982636774721482813, 982636777057693717],
                }
            ]
        }
