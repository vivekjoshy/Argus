from queue import Queue

import discord
from discord import Interaction, Embed
from discord.app_commands import (
    AppCommandError,
    MissingAnyRole,
    MissingRole,
    MissingPermissions,
    CommandOnCooldown,
)
from discord.ext import commands

from argus.formatter import TimeDelta
from argus.constants import BOT_DESCRIPTION, PLUGINS
from argus.utils import update


class ArgusClient(commands.Bot):
    """
    Custom implementation designed to load configuration from the TOML
    config file and dynamic console configurations
    """

    def __init__(self, config, logger, *args, **kwargs):
        # Setup Defaults
        self.config = config
        self.logger = logger
        self.db = None

        # Setup State Management
        self.state = {
            "roles_are_setup": False,
            "channels_are_setup": False,
            "map_roles": {},
            "map_channels": {},
            "debates_enabled": False,
            "debate_rooms": [],
            "debate_room_maps": [],
            "interface_messages": [],
            "exiting": False,
            "debate_feed_fifo": Queue(),
            "voice_channel_update_task": None,
            "debate_feed_updater_task": None,
            "propositions": [],
        }

        super().__init__(
            command_prefix=["$"],
            description=BOT_DESCRIPTION,
            intents=discord.Intents.all(),
            *args,
            **kwargs,
        )
        self.tree.on_error = self.app_command_error

    async def setup_hook(self):
        # Load Extensions
        for extension in PLUGINS:
            try:
                await self.load_extension(extension)
            except discord.ClientException:
                self.logger.exception(
                    f"Missing setup() for Plugin", extension=extension
                )
            except ImportError:
                self.logger.exception(f"Failed to load Plugin", extension=extension)
            except Exception as e:
                self.logger.exception("Core Error")

    async def app_command_error(self, interaction: Interaction, error: AppCommandError):
        if isinstance(error, MissingAnyRole):
            await update(
                interaction,
                embed=Embed(
                    title="Command Unauthorized",
                    description="You are not authorized to run this command.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return
        if isinstance(error, MissingRole):
            await update(
                interaction,
                embed=Embed(
                    title="Command Unauthorized",
                    description="You are not authorized to run this command.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return
        if isinstance(error, MissingPermissions):
            await update(
                interaction,
                embed=Embed(
                    title="Command Unauthorized",
                    description="You are not authorized to run this command.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if isinstance(error, CommandOnCooldown):
            time_left = TimeDelta(seconds=round(error.retry_after))
            await update(
                interaction,
                embed=Embed(
                    title="Command On Cooldown",
                    description=f"You are not authorized to run this command for another {time_left}.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        self.logger.exception(f"{error}", exc_info=error)
