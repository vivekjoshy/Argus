import asyncio
import datetime

import discord
import pytz
from discord import app_commands, Embed, Permissions
from discord.ext import commands

from argus.checks import check_prerequisites_enabled
from argus.client import ArgusClient
from argus.common import send_embed_message
from argus.constants import ROLE_PERMISSIONS
from argus.db.models.guild import GuildModel
from argus.models import DebateRoom
from argus.overwrites import generate_overwrites
from argus.tasks import debate_feed_updater
from argus.utils import update
from argus.voice import voice_channel_update


@app_commands.default_permissions(administrator=True)
class Lockdown(commands.GroupCog, name="lockdown"):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name="start",
        description="Start a lockdown for the entire server.",
    )
    @check_prerequisites_enabled()
    async def start(self, interaction: discord.Interaction) -> None:
        await update(
            interaction,
            embed=Embed(
                title="Locking Server",
                description="This may take a while.",
                color=0xF1C40F,
            ),
        )

        # Shortcut Variables
        channels = self.bot.state["map_channels"]
        roles = self.bot.state["map_roles"]

        roles["role_judge"] = discord.utils.get(interaction.guild.roles, name="Judge")
        roles["role_citizen"] = discord.utils.get(
            interaction.guild.roles, name="Citizen"
        )
        roles["role_member"] = discord.utils.get(interaction.guild.roles, name="Member")
        roles["role_everyone"] = interaction.guild.default_role

        await roles["role_citizen"].edit(
            permissions=Permissions(permissions=137474982912)
        )
        await roles["role_citizen"].edit(
            permissions=Permissions(permissions=137474982912)
        )
        await roles["role_member"].edit(
            permissions=Permissions(permissions=137474982912)
        )
        await roles["role_everyone"].edit(permissions=Permissions(permissions=35718144))

        debate_rooms = self.bot.state["debate_rooms"]

        for room in debate_rooms:
            if room.match:
                room.match = None
            room.purge_topics()

            for member in room.vc.members:
                await member.edit(voice_channel=None)

        self.bot.state["debates_enabled"] = False
        self.bot.state["interface_messages"] = []

        for room in debate_rooms:
            now = datetime.datetime.now(tz=pytz.UTC)
            async for message in room.vc.history(
                limit=100, after=now - datetime.timedelta(days=14)
            ):
                if message.author == self.bot.user:
                    if len(message.embeds) > 0:
                        if message.embeds[0].title.startswith("Debate Room"):
                            await message.delete()

        # Send Confirmation Message
        await update(
            interaction,
            embed=Embed(
                title="Lockdown Started",
                description="Server is currently on lockdown. Only staff can interact with the server.",
                color=0x2ECC71,
            ),
        )

    @app_commands.command(
        name="end",
        description="Ends the lockdown of the entire server.",
    )
    @check_prerequisites_enabled()
    async def end(self, interaction: discord.Interaction) -> None:
        await update(
            interaction,
            embed=Embed(
                title="Unlocking Server",
                description="This may take a while.",
                color=0xF1C40F,
            ),
        )

        # Reset Variables
        self.bot.state["debate_rooms"] = []
        self.bot.state["debate_room_maps"] = []
        self.bot.state["interface_messages"] = []

        # Shortcut Variables
        channels = self.bot.state["map_channels"]
        roles = self.bot.state["map_roles"]
        debate_rooms = self.bot.state["debate_rooms"]
        debate_room_maps = self.bot.state["debate_room_maps"]
        interface_messages = self.bot.state["interface_messages"]
        guild = interaction.guild

        guild_data: GuildModel = await self.bot.engine.find_one(
            GuildModel, GuildModel.guild == guild.id
        )
        for channel_number in range(1, 21):
            vc_debate_key = f"vc_debate_{channel_number}"
            if vc_debate_key in guild_data.channels.keys():
                vc = self.bot.get_channel(guild_data.channels[vc_debate_key])
                debate_rooms.append(
                    DebateRoom(
                        channel_number,
                        vc,
                    )
                )

        roles["role_judge"] = discord.utils.get(interaction.guild.roles, name="Judge")
        roles["role_citizen"] = discord.utils.get(
            interaction.guild.roles, name="Citizen"
        )
        roles["role_member"] = discord.utils.get(interaction.guild.roles, name="Member")
        roles["role_everyone"] = interaction.guild.default_role

        await roles["role_judge"].edit(
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_judge"])
        )

        await roles["role_citizen"].edit(
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_citizen"])
        )
        await roles["role_member"].edit(
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_member"])
        )
        await roles["role_everyone"].edit(
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_everyone"])
        )

        for room in debate_rooms:
            if room.match:
                room.match = None
            room.purge_topics()

            for member in room.vc.members:
                await member.edit(voice_channel=None)

        for room in debate_rooms:
            now = datetime.datetime.now(tz=pytz.UTC)
            async for message in room.vc.history(
                limit=100, after=now - datetime.timedelta(days=14)
            ):
                if message.author == self.bot.user:
                    if len(message.embeds) > 0:
                        if message.embeds[0].title.startswith("Debate Room"):
                            await message.delete()

        for room in debate_rooms:
            message = await send_embed_message(self.bot, room.number)
            interface_messages.append(message.id)

        debate_feed_updated_task = self.bot.state["debate_feed_updater_task"]
        voice_channel_update_task = self.bot.state["voice_channel_update_task"]

        if debate_feed_updated_task:
            debate_feed_updated_task.cancel()
            self.bot.state["debate_feed_updater_task"] = asyncio.create_task(
                debate_feed_updater(self.bot)
            )
        else:
            self.bot.state["debate_feed_updater_task"] = asyncio.create_task(
                debate_feed_updater(self.bot)
            )

        if voice_channel_update_task:
            voice_channel_update_task.cancel()
            self.bot.state["voice_channel_update_task"] = asyncio.create_task(
                voice_channel_update(self.bot)
            )
        else:
            self.bot.state["voice_channel_update_task"] = asyncio.create_task(
                voice_channel_update(self.bot)
            )

        self.bot.state["debates_enabled"] = True

        # Send Confirmation Message
        await update(
            interaction,
            embed=Embed(
                title="Lockdown Ended",
                description="Server is back open for business.",
                color=0x2ECC71,
            ),
        )


async def setup(bot: ArgusClient) -> None:
    await bot.add_cog(
        Lockdown(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
