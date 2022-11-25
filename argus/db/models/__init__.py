from discord import Guild, Member, Role
from discord.abc import GuildChannel

from argus.app import bot


class DiscordGuild(int):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, Guild):
            return int(v.id)
        elif isinstance(v, int):
            guild = bot.get_guild(v)
            if guild:
                return int(guild.id)
            else:
                ValueError(f"Guild {v} not in cache.")
        else:
            ValueError(f"Guild IDs must be of type `int` or `discord.Guild`")


class DiscordRole(int):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, Role):
            return int(v.id)
        elif isinstance(v, int):
            return int(v)
        else:
            return ValueError(f"Role IDs must be of type `int`.")


class DiscordChannel(int):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, GuildChannel):
            return int(v.id)
        if isinstance(v, int):
            return v
        else:
            return ValueError(f"Channel IDs must be of type `int`.")


class DiscordMember(int):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, Member):
            return int(v.id)
        if isinstance(v, int):
            return v
        else:
            return ValueError(f"Member IDs must be of type `int`.")
