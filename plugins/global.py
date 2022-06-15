import datetime
from typing import List

import discord
import pytz
from discord import app_commands, Interaction, Embed
from discord.ext import commands

from argus.client import ArgusClient
from argus.common import send_embed_message, check_roles_exist
from argus.db.models.guild import GuildModel
from argus.models import DebateRoom
from argus.utils import update


@app_commands.default_permissions(administrator=True)
class Global(
    commands.GroupCog, name="global", description="Handle global functions of the bot."
):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info(
            f"Logged In", username=self.bot.user.name, user_id=self.bot.user.id
        )
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="over Debates"
            )
        )

    @app_commands.command(
        name="enable",
        description="Enable the bot for server users.",
    )
    async def enable(self, interaction: Interaction) -> None:
        await update(
            interaction,
            embed=Embed(
                title="Enabling Argus",
                description="This may take a while.",
                color=0xF1C40F,
            ),
        )

        self.bot.state["debates_enabled"] = True
        debate_rooms: List[DebateRoom] = self.bot.state["debate_rooms"]
        roles = self.bot.state["map_roles"]
        interface_messages = self.bot.state["interface_messages"]
        guild = interaction.guild

        roles_exist = await check_roles_exist(self.bot, interaction)

        if not roles_exist:
            await update(
                interaction,
                embed=Embed(
                    title="Data Mismatch",
                    description="Please run the setup of roles again. "
                    "Roles in the server do not match the database.",
                    color=0xE74C3C,
                ),
            )
            return

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

        for room in debate_rooms:
            now = datetime.datetime.now(tz=pytz.UTC)
            async for message in room.vc.history(
                limit=100, after=now - datetime.timedelta(days=14)
            ):
                if message.author == self.bot.user:
                    if message.embeds[0].title.startswith("Debate Room"):
                        await message.delete()

        for room in debate_rooms:
            message = await send_embed_message(self.bot, room.number)
            interface_messages.append(message.id)

        # Send Confirmation Message
        await update(
            interaction,
            embed=Embed(
                title="Argus Enabled",
                description="All functions of this bot have been enabled.",
                colour=0x2ECC71,
            ),
        )


async def setup(bot: ArgusClient) -> None:
    await bot.add_cog(
        Global(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
