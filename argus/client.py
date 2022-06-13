from queue import Queue

import discord
from discord.ext import commands

from argus.constants import BOT_DESCRIPTION, PLUGINS


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
            "debate_room_tcs": [],
            "interface_messages": [],
            "exiting": False,
            "debate_feed_fifo": Queue(),
            "voice_channel_update_task": None,
            "debate_feed_updater_task": None,
            "vc_create_room": 0,
            "map_lounge_vcs": {},
            "map_lounge_vc_to_tc": {},
            "map_delete_lounge_room": {},
            "presentation_sc": None,
            "presentation_chat_tc": None,
            "presentation_questions": None,
            "events_vc": None,
            "events_tc_1": None,
            "events_tc_2": None,
        }

        super().__init__(
            command_prefix=["$"],
            description=BOT_DESCRIPTION,
            intents=discord.Intents.all(),
            *args,
            **kwargs,
        )

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
