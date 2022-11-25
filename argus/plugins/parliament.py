import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

import discord
from cachetools import TTLCache
from discord import Embed, Interaction, Member, app_commands
from discord.ext.commands import GroupCog

from argus.client import ArgusClient
from argus.modals import MotionProposal
from argus.utils import update


class Motion(GroupCog, name="motion"):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot

        self.hl_motion = TTLCache(
            maxsize=1, ttl=timedelta(hours=24), timer=datetime.now
        )
        self.hc_motion = TTLCache(
            maxsize=1, ttl=timedelta(hours=24), timer=datetime.now
        )

        self.hl_last_embed: Optional[Embed] = None
        self.hc_last_embed: Optional[Embed] = None

        self.hl_id = None
        self.hc_id = None

        self.hl = None
        self.hc = None
        self.motions = None

        self.hl_enabled = False
        self.hc_enabled = False

        self.hl_yes: List[Member] = []
        self.hl_no: List[Member] = []

        self.hc_yes: List[Member] = []
        self.hc_no: List[Member] = []

        self.bot.loop.create_task(self.motion_expiry_task())

    @app_commands.command(
        name="propose",
        description="Propose a new motion to parliament.",
    )
    @app_commands.checks.has_any_role(
        "The Crown", "Chancellor", "Liege", "Prime Minister", "Minister"
    )
    async def propose(self, interaction: Interaction) -> None:
        channel = interaction.channel
        self.hl = discord.utils.get(interaction.guild.channels, name="House of Lords")
        self.hc = discord.utils.get(interaction.guild.channels, name="House of Commons")
        self.motions = discord.utils.get(interaction.guild.channels, name="motions")

        if channel not in [self.hl, self.hc]:
            await update(
                interaction,
                embed=Embed(
                    title="Incorrect Channel",
                    description="You can only propose motions under parliament.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        self.hl_motion.expire()
        self.hc_motion.expire()
        if "embed" in self.hl_motion or "embed" in self.hc_motion:
            await update(
                interaction,
                embed=Embed(
                    title="Existing Motion Found",
                    description="Only one motion can be deliberated at a time.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if channel == self.hl:
            self.hl_enabled = True
            await interaction.response.send_modal(MotionProposal(states=self))
            return

        if channel == self.hc:
            self.hc_enabled = True
            await interaction.response.send_modal(MotionProposal(states=self))
            return

    async def motion_expiry_task(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(self.bot.config["global"]["guild_id"])
        self.motions = discord.utils.get(guild.channels, name="motions")
        while True:
            self.hl_motion.expire()
            self.hc_motion.expire()
            if "embed" in self.hl_motion or "embed" in self.hc_motion:
                pass
            else:
                if self.hl_last_embed:
                    liege = discord.utils.get(guild.roles, name="Liege")
                    hl_members = liege.members
                    required_votes = (len(hl_members) + 1) / 50
                    total_members = len(hl_members) + 1
                    if len(self.hl_yes) / total_members > required_votes:
                        self.hl_last_embed.title = f"Motion Passed - {self.hl_id}"
                        self.hl_last_embed.color = 0x2ECC71
                        await self.motions.send(embeds=[self.hl_last_embed])
                        self.hl_motion.popitem()
                        self.hl_last_embed = None
                        self.hl_yes = []
                        self.hl_no = []
                        self.hl_id = None
                    elif len(self.hl_no) / total_members > required_votes:
                        self.hl_last_embed.title = f"Motion Failed - {self.hl_id}"
                        self.hl_last_embed.color = 0xE74C3C
                        await self.motions.send(embeds=[self.hl_last_embed])
                        self.hl_motion.popitem()
                        self.hl_last_embed = None
                        self.hl_yes = []
                        self.hl_no = []
                        self.hl_id = None
                elif self.hc_last_embed:
                    minister = discord.utils.get(guild.roles, name="Minister")
                    hc_members = minister.members
                    required_votes = (len(hc_members) + 1) / 50
                    total_members = len(hc_members) + 1
                    if len(self.hc_yes) / total_members > required_votes:
                        self.hc_last_embed.title = f"Motion Passed - {self.hc_id}"
                        self.hc_last_embed.color = 0x2ECC71
                        await self.motions.send(embeds=[self.hc_last_embed])
                        self.hc_motion.popitem()
                        self.hc_last_embed = None
                        self.hc_yes = []
                        self.hc_no = []
                        self.hc_id = None
                    elif len(self.hc_no) / total_members > required_votes:
                        self.hc_last_embed.title = f"Motion Failed - {self.hc_id}"
                        self.hc_last_embed.color = 0xE74C3C
                        await self.motions.send(embeds=[self.hc_last_embed])
                        self.hc_motion.popitem()
                        self.hc_last_embed = None
                        self.hc_yes = []
                        self.hc_no = []
                        self.hc_id = None
            await asyncio.sleep(5)

    @app_commands.command(
        name="yes",
        description="Vote yes to pass the current motion.",
    )
    @app_commands.checks.has_any_role(
        "The Crown", "Chancellor", "Liege", "Prime Minister", "Minister"
    )
    async def yes(self, interaction: Interaction) -> None:
        channel = interaction.channel
        self.hl = discord.utils.get(interaction.guild.channels, name="House of Lords")
        self.hc = discord.utils.get(interaction.guild.channels, name="House of Commons")
        self.motions = discord.utils.get(interaction.guild.channels, name="motions")

        if channel not in [self.hl, self.hc]:
            await update(
                interaction,
                embed=Embed(
                    title="Incorrect Channel",
                    description="You can only propose motions under parliament.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if channel == self.hl:
            if interaction.user not in self.hl_yes:
                self.hl_yes.append(interaction.user)
            if interaction.user in self.hl_no:
                self.hl_no.remove(interaction.user)

            liege = discord.utils.get(interaction.guild.roles, name="Liege")
            hl_members = liege.members
            required_votes = (len(hl_members) + 1) / 50
            total_members = len(hl_members) + 1
            if len(self.hl_yes) / total_members > required_votes:
                self.hl_last_embed.title = f"Motion Passed - {self.hl_id}"
                self.hl_last_embed.color = 0x2ECC71
                await self.motions.send(embeds=[self.hl_last_embed])
                self.hl_motion.popitem()
                self.hl_last_embed = None
                self.hl_yes = []
                self.hl_no = []
                self.hl_id = None
            elif len(self.hl_no) / total_members > required_votes:
                self.hl_last_embed.title = f"Motion Failed - {self.hl_id}"
                self.hl_last_embed.color = 0xE74C3C
                await self.motions.send(embeds=[self.hl_last_embed])
                self.hl_motion.popitem()
                self.hl_last_embed = None
                self.hl_yes = []
                self.hl_no = []
                self.hl_id = None

        elif channel == self.hc:
            if interaction.user not in self.hc_yes:
                self.hc_yes.append(interaction.user)
            if interaction.user in self.hc_no:
                self.hc_no.remove(interaction.user)

            minister = discord.utils.get(interaction.guild.roles, name="Minister")
            hc_members = minister.members
            required_votes = (len(hc_members) + 1) / 50
            total_members = len(hc_members) + 1
            if len(self.hc_yes) / total_members > required_votes:
                self.hc_last_embed.title = f"Motion Passed - {self.hc_id}"
                self.hc_last_embed.color = 0x2ECC71
                await self.motions.send(embeds=[self.hc_last_embed])
                self.hc_motion.popitem()
                self.hc_last_embed = None
                self.hc_yes = []
                self.hc_no = []
                self.hc_id = None
            elif len(self.hc_no) / total_members > required_votes:
                self.hc_last_embed.title = f"Motion Failed - {self.hc_id}"
                self.hc_last_embed.color = 0xE74C3C
                await self.motions.send(embeds=[self.hc_last_embed])
                self.hc_motion.popitem()
                self.hc_last_embed = None
                self.hc_yes = []
                self.hc_no = []
                self.hc_id = None

        embed = Embed(
            title="Motion Voted",
            description="You have voted 'yes' on the current motion.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed, ephemeral=True)

    @app_commands.command(
        name="no",
        description="Vote no to fail the current motion.",
    )
    @app_commands.checks.has_any_role(
        "The Crown", "Chancellor", "Liege", "Prime Minister", "Minister"
    )
    async def no(self, interaction: Interaction) -> None:
        channel = interaction.channel
        self.hl = discord.utils.get(interaction.guild.channels, name="House of Lords")
        self.hc = discord.utils.get(interaction.guild.channels, name="House of Commons")
        self.motions = discord.utils.get(interaction.guild.channels, name="motions")

        if channel not in [self.hl, self.hc]:
            await update(
                interaction,
                embed=Embed(
                    title="Incorrect Channel",
                    description="You can only propose motions under parliament.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if channel == self.hl:
            if interaction.user not in self.hl_no:
                self.hl_no.append(interaction.user)
            if interaction.user in self.hl_yes:
                self.hl_yes.remove(interaction.user)

            liege = discord.utils.get(interaction.guild.roles, name="Liege")
            hl_members = liege.members
            required_votes = (len(hl_members) + 1) / 50
            total_members = len(hl_members) + 1
            if len(self.hl_yes) / total_members > required_votes:
                self.hl_last_embed.title = f"Motion Passed - {self.hl_id}"
                self.hl_last_embed.color = 0x2ECC71
                await self.motions.send(embeds=[self.hl_last_embed])
                self.hl_motion.popitem()
                self.hl_last_embed = None
                self.hl_yes = []
                self.hl_no = []
                self.hl_id = None
            elif len(self.hl_no) / total_members > required_votes:
                self.hl_last_embed.title = f"Motion Failed - {self.hl_id}"
                self.hl_last_embed.color = 0xE74C3C
                await self.motions.send(embeds=[self.hl_last_embed])
                self.hl_motion.popitem()
                self.hl_last_embed = None
                self.hl_yes = []
                self.hl_no = []
                self.hl_id = None
        elif channel == self.hc:
            if interaction.user not in self.hc_no:
                self.hc_no.append(interaction.user)
            if interaction.user in self.hc_yes:
                self.hc_yes.remove(interaction.user)

            minister = discord.utils.get(interaction.guild.roles, name="Minister")
            hc_members = minister.members
            required_votes = (len(hc_members) + 1) / 50
            total_members = len(hc_members) + 1
            if len(self.hc_yes) / total_members > required_votes:
                self.hc_last_embed.title = f"Motion Passed - {self.hc_id}"
                self.hc_last_embed.color = 0x2ECC71
                await self.motions.send(embeds=[self.hc_last_embed])
                self.hc_motion.popitem()
                self.hc_last_embed = None
                self.hc_yes = []
                self.hc_no = []
                self.hc_id = None
            elif len(self.hc_no) / total_members > required_votes:
                self.hc_last_embed.title = f"Motion Failed - {self.hc_id}"
                self.hc_last_embed.color = 0xE74C3C
                await self.motions.send(embeds=[self.hc_last_embed])
                self.hc_motion.popitem()
                self.hc_last_embed = None
                self.hc_yes = []
                self.hc_no = []
                self.hc_id = None

        embed = Embed(
            title="Motion Voted",
            description="You have voted 'no' on the current motion.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed, ephemeral=True)

    @app_commands.command(
        name="kill",
        description="Kill a motion.",
    )
    @app_commands.checks.has_any_role(
        "The Crown",
    )
    async def kill(self, interaction: Interaction) -> None:
        channel = interaction.channel
        self.hl = discord.utils.get(interaction.guild.channels, name="House of Lords")
        self.hc = discord.utils.get(interaction.guild.channels, name="House of Commons")
        self.motions = discord.utils.get(interaction.guild.channels, name="motions")

        if channel not in [self.hl, self.hc]:
            await update(
                interaction,
                embed=Embed(
                    title="Incorrect Channel",
                    description="You can only kill motions under parliament.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if channel == self.hl:
            self.hl_last_embed = None
            self.hl_yes = []
            self.hl_no = []
            self.hl_motion.popitem()

            embed = Embed(
                title=f"Motion Killed - {self.hl_id}",
                description="This motion has been vetoed.",
                color=0xE74C3C,
            )
            await self.motions.send(embeds=[embed])
            self.hl_id = None
        elif channel == self.hc:
            self.hc_last_embed = None
            self.hc_yes = []
            self.hc_no = []
            self.hc_motion.popitem()

            embed = Embed(
                title=f"Motion Killed - {self.hc_id}",
                description="This motion has been vetoed.",
                color=0xE74C3C,
            )
            await self.motions.send(embeds=[embed])
            self.hc_id = None

        embed = Embed(
            title="Motion Vetoed",
            description="You have vetoed the current motion.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed, ephemeral=True)


async def setup(bot: ArgusClient) -> None:
    await bot.add_cog(
        Motion(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
