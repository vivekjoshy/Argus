import asyncio
import io
import math
import random
import typing
from datetime import datetime
from queue import Queue
from typing import Optional

import discord
import matplotlib.pyplot as plt
import numpy as np
import openskill
import pymongo
from discord import app_commands, Member, Interaction, Embed, Role
from discord.app_commands import (
    MissingRole,
    MissingAnyRole,
    MissingPermissions,
    AppCommandError,
)
from discord.ext import commands
from matplotlib import ticker

from argus.client import ArgusClient
from argus.common import (
    insert_skill,
    get_room_number,
    in_debate_room,
    unlocked_in_private_room,
    get_room,
    update_im,
    update_topic,
    check_debater_in_any_room,
    get_debater_room,
    consented,
    add_interface_message,
    in_commands_or_debate,
)
from argus.constants import RANK_RATING_MAP
from argus.db.models.user import MemberModel
from argus.modals import DebateVotingRubric
from argus.models import DebateRoom, DebateTopic, DebateParticipant
from argus.utils import update, floor_rating, normalize


@app_commands.default_permissions(send_messages=True)
class Skill(
    commands.GroupCog,
    name="skill",
    description="Display your skill as assessed by the system.",
):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name="view",
        description="Display the skill of a user as assessed by the system.",
    )
    async def view(
        self, interaction: Interaction, member: Optional[Member] = None
    ) -> None:
        command = discord.utils.get(interaction.guild.channels, name="commands")
        if member:
            if member.bot:
                embed = Embed(
                    title=f"Incorrect User Type",
                    description="Please run this command against a user that is not a bot.",
                    color=0xE74C3C,
                )
                await update(interaction, embed=embed, ephemeral=True)
            else:
                packed_data = await insert_skill(self.bot, interaction, member)
                pipeline = [
                    {"$sort": {"rating": -1}},
                    {"$group": {"_id": None, "items": {"$push": "$$ROOT"}}},
                    {"$unwind": {"path": "$items", "includeArrayIndex": "items.rank"}},
                    {"$replaceRoot": {"newRoot": "$items"}},
                    {"$addFields": {"newRank": {"$add": ["$rank", 1]}}},
                    {"$match": {"member": int(member.id)}},
                ]

                member_found = None
                member_doc = self.bot.db[self.bot.db.database].member.aggregate(
                    pipeline=pipeline
                )
                async for member_found in member_doc:
                    break

                if not member_found:
                    embed = Embed(
                        title="Unknown Error",
                        description="Database seems to be corrupt. Please contact an engineer.",
                        color=0xE74C3C,
                    )
                    await update(interaction, embed=embed, ephemeral=True)
                    return

                mu = packed_data["mu"]
                sigma = packed_data["sigma"]
                rating = packed_data["rating"]
                current_rank_role = packed_data["current_rank_role"]
                rank = current_rank_role

                member_data = await self.bot.engine.find_one(
                    MemberModel, MemberModel.member == member.id
                )
                y = {
                    "Factual": member_data.factual,
                    "Consistent": member_data.consistent,
                    "Charitable": member_data.charitable,
                    "Respectful": member_data.respectful,
                }
                y = normalize(y)
                plt.style.use("ggplot")
                fig, ax = plt.subplots()
                ax.barh(list(y.keys()), list(y.values()))
                plt.tight_layout()
                ax.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
                buffer = io.BytesIO()
                plt.savefig(buffer, format="png")
                buffer.seek(0)
                file = discord.File(fp=buffer, filename="graph.png")

                avatar_url = None
                if member.avatar:
                    avatar_url = member.avatar.url
                embed = Embed(title="Skill Rating", color=0xEC6A5C)
                embed.set_footer(text=member.display_name, icon_url=avatar_url)
                embed.set_image(url="attachment://graph.png")
                embed.add_field(
                    name="Mean",
                    value=f"```{mu: .2f}```",
                    inline=True,
                )
                embed.add_field(
                    name="Confidence",
                    value=f"```{sigma: .2f}```",
                    inline=True,
                )
                embed.add_field(
                    name="Rating",
                    value=f"```{20 * ((mu - 3 * sigma) + 25): .2f}```",
                    inline=True,
                )
                embed.add_field(
                    name="Rank",
                    value=f"```{str(member_found['rank'] + 1)}```",
                    inline=True,
                )
                embed.add_field(name="Title", value=f"```{rank.name}```", inline=True)
                embed.add_field(
                    name="Vote Count",
                    value=f"```{member_data.vote_count}```",
                    inline=True,
                )
                if interaction.channel == command:
                    await update(interaction, file=file, embed=embed)
                else:
                    await update(interaction, file=file, embed=embed, ephemeral=True)
        else:
            packed_data = await insert_skill(self.bot, interaction, interaction.user)
            pipeline = [
                {"$sort": {"rating": -1}},
                {"$group": {"_id": None, "items": {"$push": "$$ROOT"}}},
                {"$unwind": {"path": "$items", "includeArrayIndex": "items.rank"}},
                {"$replaceRoot": {"newRoot": "$items"}},
                {"$addFields": {"newRank": {"$add": ["$rank", 1]}}},
                {"$match": {"member": int(interaction.user.id)}},
            ]

            member_found = None
            member_doc = self.bot.db[self.bot.db.database].member.aggregate(
                pipeline=pipeline
            )
            async for member_found in member_doc:
                break

            if not member_found:
                embed = Embed(
                    title="Unknown Error",
                    description="Database seems to be corrupt. Please contact an engineer.",
                    color=0xE74C3C,
                )
                await update(interaction, embed=embed, ephemeral=True)
                return

            mu = packed_data["mu"]
            sigma = packed_data["sigma"]
            rating = packed_data["rating"]
            current_rank_role = packed_data["current_rank_role"]
            rank = current_rank_role

            member_data = await self.bot.engine.find_one(
                MemberModel, MemberModel.member == interaction.user.id
            )
            y = {
                "Factual": member_data.factual,
                "Consistent": member_data.consistent,
                "Charitable": member_data.charitable,
                "Respectful": member_data.respectful,
            }
            y = normalize(y)
            plt.style.use("ggplot")
            fig, ax = plt.subplots()
            ax.barh(list(y.keys()), list(y.values()))
            plt.tight_layout()
            ax.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
            buffer = io.BytesIO()
            plt.savefig(
                buffer,
                format="png",
            )
            buffer.seek(0)
            file = discord.File(fp=buffer, filename="graph.png")

            avatar_url = None
            if interaction.user.avatar:
                avatar_url = interaction.user.avatar.url
            embed = Embed(title="Skill Rating", color=0xEC6A5C)
            embed.set_footer(text=interaction.user.display_name, icon_url=avatar_url)
            embed.set_image(url="attachment://graph.png")
            embed.add_field(
                name="Mean",
                value=f"```{mu: .2f}```",
                inline=True,
            )
            embed.add_field(
                name="Confidence",
                value=f"```{sigma: .2f}```",
                inline=True,
            )
            embed.add_field(
                name="Rating",
                value=f"```{20 * ((mu - 3 * sigma) + 25): .2f}```",
                inline=True,
            )
            embed.add_field(
                name="Rank", value=f"```{str(member_found['rank'] + 1)}```", inline=True
            )
            embed.add_field(name="Title", value=f"```{rank.name}```", inline=True)
            embed.add_field(
                name="Vote Count", value=f"```{member_data.vote_count}```", inline=True
            )
            if interaction.channel == command:
                await update(interaction, file=file, embed=embed)
            else:
                await update(interaction, file=file, embed=embed, ephemeral=True)

    @app_commands.command(
        name="compare",
        description="Get the probability of one player winning against another.",
    )
    async def compare(
        self,
        interaction: Interaction,
        player_a: Optional[Member] = None,
        player_b: Optional[Member] = None,
    ) -> None:
        if not await in_commands_or_debate(self.bot, interaction):
            return

        if player_a.bot or player_b.bot:
            embed = Embed(
                title=f"Incorrect User Type",
                description="Please run this command against a user that is not a bot.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        player_a_data = await insert_skill(self.bot, interaction, player_a)
        player_b_data = await insert_skill(self.bot, interaction, player_b)

        mu_a = player_a_data["mu"]
        sigma_a = player_a_data["sigma"]
        rating_a = player_a_data["rating"]
        current_rank_role_a = player_a_data["current_rank_role"]

        mu_b = player_b_data["mu"]
        sigma_b = player_b_data["sigma"]
        rating_b = player_b_data["rating"]
        current_rank_role_b = player_b_data["current_rank_role"]

        player_a_rating = openskill.create_rating([mu_a, sigma_a])
        player_b_rating = openskill.create_rating([mu_b, sigma_b])
        player_a_probability, player_b_probability = openskill.predict_win(
            teams=[[player_a_rating], [player_b_rating]]
        )
        draw_probability = openskill.predict_draw(
            teams=[[player_a_rating], [player_b_rating]]
        )
        if player_a_probability > player_b_probability:
            embed = Embed(title="Predictions", color=0xEC6A5C)
            embed.add_field(
                name="Win Probability",
                value=f"{player_a.mention} has a "
                f"{((player_a_probability - player_b_probability) / player_b_probability) * 100: .2f}% "
                f"chance of winning against {player_b.mention}.",
                inline=False,
            )
            embed.add_field(
                name="Draw Probability",
                value=f"The debate has a {draw_probability: .2f}% chance of drawing.",
                inline=False,
            )
            embed.add_field(
                name="Raw Probabilities",
                value=f"`{1: 03d}` {player_a.mention} • {player_a_probability * 100: .2f}%\n"
                f"`{2: 03d}` {player_b.mention} • {player_b_probability * 100: .2f}%",
                inline=False,
            )
            await update(interaction, embed=embed)
        elif player_a_probability < player_b_probability:
            embed = Embed(title="Win Predictions", color=0xEC6A5C)
            embed.add_field(
                name="Win Probability",
                value=f"{player_b.mention} has a "
                f"{((player_b_probability - player_a_probability) / player_a_probability) * 100: .2f}% "
                f"chance of winning against {player_a.mention}.",
                inline=False,
            )
            embed.add_field(
                name="Draw Probability",
                value=f"The debate has a {draw_probability: .2f}% chance of drawing.",
                inline=False,
            )
            embed.add_field(
                name="Win Probabilities",
                value=f"`{1: 03d}` {player_a.mention} • {player_a_probability * 100: .2f}%\n"
                f"`{2: 03d}` {player_b.mention} • {player_b_probability * 100: .2f}%",
                inline=False,
            )
            await update(interaction, embed=embed)
        else:
            embed = Embed(title="Win Predictions", color=0xEC6A5C)
            embed.add_field(
                name="Win Probability",
                value=f"There isn't enough data to determine who will win.",
                inline=False,
            )
            embed.add_field(
                name="Draw Probability",
                value=f"The debate has a {draw_probability: .2f}% chance of drawing.",
                inline=False,
            )

            embed.add_field(
                name="Raw Probabilities",
                value=f"`{1: 03d}` {player_a.mention} • {player_a_probability * 100: .2f}%\n"
                f"`{2: 03d}` {player_b.mention} • {player_b_probability * 100: .2f}%",
                inline=False,
            )
            await update(interaction, embed=embed)

    @app_commands.command(
        name="leaderboard",
        description="Display the top 10 highest skilled players.",
    )
    async def leaderboard(
        self,
        interaction: Interaction,
    ) -> None:
        if not await in_commands_or_debate(self.bot, interaction):
            return

        skill_cursor = (
            self.bot.db[self.bot.db.database]
            .member.find()
            .sort("rating", pymongo.DESCENDING)
        )

        guild = interaction.guild
        description = ""
        count = 0
        async for skill_mapping in skill_cursor:
            if count == 10:
                break
            member = guild.get_member(skill_mapping["member"])
            if not member:
                continue
            count += 1
            description += (
                f"`{count: 03d}` {member.mention} • {skill_mapping['rating']: .2f}\n"
            )

        embed = Embed(
            title="Rating Leaderboard",
            description=description,
            color=0xEC6A5C,
        )
        await update(interaction, embed=embed)

    @app_commands.command(
        name="repair",
        description="Repair the skill of a user.",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def repair(self, interaction: Interaction, member: Member) -> None:
        await interaction.response.defer()
        if member.bot:
            embed = Embed(
                title=f"Incorrect User Type",
                description="Please run this command against a user that is not a bot.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
        else:
            await insert_skill(self.bot, interaction, member)
            embed = Embed(
                title="Skill Successfully Repaired",
                description="The user's skill has been re-initialized.",
                color=0x2ECC71,
            )
            await update(interaction, embed=embed, ephemeral=True)

    @app_commands.command(
        name="setup",
        description="Initialize the skills of members in a blank server.",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: Interaction) -> None:
        members = interaction.guild.members

        count = 0
        embed = Embed(
            title="Processing Members",
            description=f"Count: {count}",
            color=0xF1C40F,
        )
        await update(interaction, embed=embed)

        for member in members:
            if member.bot:
                continue

            await insert_skill(self.bot, interaction, member)
            count += 1

            embed = Embed(
                title="Processing Members",
                description=f"Count: {count}",
                color=0xF1C40F,
            )
            await update(interaction, embed=embed)

        embed = Embed(
            title="Creating Indexes",
            description=f"Sorting member skill ratings in descending order.",
            color=0xF1C40F,
        )
        await update(interaction, embed=embed)

        await self.bot.db[self.bot.db.database].member.create_index(
            [("rating", pymongo.DESCENDING)]
        )

        embed = Embed(
            title="Skill Successfully Set Up",
            description="User skills have been initialized.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed, ephemeral=True)


@app_commands.default_permissions(send_messages=True, connect=True)
class Topic(
    commands.GroupCog,
    name="topic",
    description="Set and vote on different kinds of topics.",
):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_error(self, interaction: Interaction, error: AppCommandError):
        if isinstance(error, MissingAnyRole):
            await update(
                interaction,
                embed=Embed(
                    title="Command Unauthorized",
                    description="You are not authorized to run this command.",
                    color=0xE74C3C,
                ),
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
            )
            return

    @app_commands.command(
        name="propose",
        description="Initialize the skills of members in a blank server.",
    )
    async def propose(self, interaction: Interaction, topic: str) -> None:
        if len(topic) > 300:
            await update(
                interaction,
                embed=Embed(
                    title=f"Setting Topic Failed",
                    description="Your topic must be less than or equal to 300 characters.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return
        if not await unlocked_in_private_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        topic_updated = room.add_topic(
            DebateTopic(
                member=interaction.user,
                message=topic,
            )
        )
        if topic_updated:
            embed = Embed(
                title="Topic Reset",
                description=f"Note: Any votes on your topic have been reset.",
                color=0xF1C40F,
            )
            embed.add_field(name="Topic", value=f"{topic}")
            await update(
                interaction,
                embed=embed,
            )
        else:
            embed = Embed(title="Topic Added", description=f"{topic}", color=0x2ECC71)
            await update(
                interaction,
                embed=embed,
            )

        await update_im(self.bot, room_num=room.number)

        room.updating_topic = True
        await update_topic(self.bot, room)
        room.updating_topic = False

    @app_commands.command(
        name="vote",
        description="Vote for who's topic you want to be debated.",
    )
    async def vote(self, interaction: Interaction, member: Member) -> None:
        if member.bot:
            embed = Embed(
                title="Invalid User",
                description="You cannot vote for bots.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return
        if not await unlocked_in_private_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        candidate = member

        if not room.check_match():
            await update(
                interaction,
                embed=Embed(
                    title="Command Disabled",
                    description="This command only works if a debate room has a current topic.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )

        await interaction.response.defer()

        result = room.vote_topic(voter=interaction.user, candidate=candidate)

        if not result:
            embed = Embed(
                title="Topic Author Not Found",
                description="No topic was authored by the given user.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        room.updating_topic = True
        await update_topic(self.bot, room)
        room.updating_topic = False

        embed = Embed(
            title="Topic Vote Successfully Cast",
            description="Your vote for that user's topic has been registered.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed)

    @app_commands.command(
        name="view",
        description="View user's topic and it's details.",
    )
    async def view(
        self, interaction: Interaction, member: Optional[Member] = None
    ) -> None:

        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        if not member:
            member = interaction.user

        for topic in room.topics:
            if member == topic.author:
                embed = Embed(
                    title="Member Topic",
                    color=0xEC6A5C,
                )
                if topic.prioritized:
                    embed.add_field(name="Topic [Prioritized]", value=f"{str(topic)}")
                else:
                    embed.add_field(name="Topic", value=f"{str(topic)}")
                avatar_url = None
                if member.avatar:
                    avatar_url = member.avatar.url
                embed.add_field(name="Votes", value=f"{str(topic.votes)}")
                embed.set_footer(text=f"{member.display_name}", icon_url=avatar_url)
                await update(interaction, embed=embed, ephemeral=True)
                return

        embed = Embed(
            title="Topic Author Not Found",
            description="No topic was authored by the given user.",
            color=0xE74C3C,
        )
        await update(interaction, embed=embed, ephemeral=True)

    @app_commands.command(
        name="remove",
        description="View user's topic and it's details.",
    )
    @app_commands.checks.has_any_role(
        "The Crown", "Chancellor", "Liege", "Prime Minister", "Minister"
    )
    async def remove(
        self, interaction: Interaction, member: Optional[Member] = None
    ) -> None:

        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)

        if not room.check_match():
            await update(
                interaction,
                embed=Embed(
                    title="Command Disabled",
                    description="This command only works if a debate room has a current topic.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return

        await interaction.response.defer()

        if member:
            if member.bot:
                embed = Embed(
                    title=f"Incorrect User Type",
                    description="Please run this command against a user that is not a bot.",
                    color=0xE74C3C,
                )
                await update(interaction, embed=embed, ephemeral=True)
                return
            topic = room.topic_from_member(member)
            if topic:
                room.remove_topic(member)
            else:
                embed = Embed(
                    title=f"Topic Author Not Found",
                    description="Please run this command against a user that has created a topic.",
                    color=0xE74C3C,
                )
                await update(interaction, embed=embed, ephemeral=True)
                return
        else:
            topic = room.current_topic
            room.remove_topic(room.current_topic.author)

        if room.match:
            if topic == room.match.topic:
                for current_member in room.vc.members:
                    await current_member.edit(mute=True)
        else:
            embed = Embed(
                title=f"No Topic Found",
                description="Please run this command when there is a topic in the room.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        room.match = None  # Clear match
        room.updating_topic = True
        await update_topic(self.bot, room)

        if room.private:
            if room.current_topic:
                for member in room.vc.members:
                    await member.edit(mute=True)
            else:
                for member in room.vc.members:
                    if member not in room.private_debaters:
                        await member.edit(mute=True)

        room.updating_topic = False

        embed = Embed(
            title="Topic Successfully Removed",
            description="The topic you selected has been removed.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed, ephemeral=True)


class Debate(commands.Cog):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_error(self, interaction: Interaction, error: AppCommandError):
        if isinstance(error, MissingAnyRole):
            await update(
                interaction,
                embed=Embed(
                    title="Command Unauthorized",
                    description="You are not authorized to run this command.",
                    color=0xE74C3C,
                ),
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
            )
            return

    @app_commands.command(
        name="for", description="Set you stance as for the topic in a debate room."
    )
    async def stance_for(self, interaction: discord.Interaction) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        author = interaction.user

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if not room.check_match():
            await update(
                interaction,
                embed=Embed(
                    title="Command Disabled",
                    description="This command only works if a debate room has a current topic.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )

        if room.match.check_participant(author):
            participant = room.match.get_participant(author)
            if participant.against:
                embed = Embed(
                    title="Stance Already Set",
                    description="You are already against the topic.",
                    color=0xF1C40F,
                )
            else:
                embed = Embed(
                    title="Stance Already Set",
                    description="You are already for the topic.",
                    color=0xF1C40F,
                )
            await update(interaction, embed=embed, ephemeral=True)
            return

        packed_data = await insert_skill(self.bot, interaction, author)
        mu = packed_data["mu"]
        sigma = packed_data["sigma"]

        room.match.add_for(
            DebateParticipant(
                member=author, mu=mu, sigma=sigma, session_start=datetime.utcnow()
            )
        )

        embed = Embed(
            title="Stance Successfully Set",
            description="You are __for__ the topic.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed)

    @app_commands.command(
        name="against",
        description="Set you stance as against the topic in a debate room.",
    )
    async def stance_against(self, interaction: discord.Interaction) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        author = interaction.user

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        if not room.check_match():
            await update(
                interaction,
                embed=Embed(
                    title="Command Disabled",
                    description="This command only works if a debate room has a current topic.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )

        if room.match.check_participant(author):
            participant = room.match.get_participant(author)
            if participant.against:
                embed = Embed(
                    title="Stance Already Set",
                    description="You are already against the topic.",
                    color=0xF1C40F,
                )
            else:
                embed = Embed(
                    title="Stance Already Set",
                    description="You are already for the topic.",
                    color=0xF1C40F,
                )
            await update(interaction, embed=embed, ephemeral=True)
            return

        packed_data = await insert_skill(self.bot, interaction, author)
        mu = packed_data["mu"]
        sigma = packed_data["sigma"]

        room.match.add_against(
            DebateParticipant(
                member=author, mu=mu, sigma=sigma, session_start=datetime.utcnow()
            )
        )

        embed = Embed(
            title="Stance Successfully Set",
            description="You are __against__ the topic.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed)

    @app_commands.command(
        name="debate", description="Start or join a debate after you've set a stance."
    )
    async def add_debater(self, interaction: discord.Interaction) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return
        if not await unlocked_in_private_room(self.bot, interaction):
            return
        if not await consented(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        author = interaction.user

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        if not room.check_match():
            await update(
                interaction,
                embed=Embed(
                    title="Command Disabled",
                    description="This command only works if a debate room has a current topic.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )

        if check_debater_in_any_room(
            bot=self.bot, interaction=interaction, room=room, member=author
        ):
            debater_room = get_debater_room(
                bot=self.bot, interaction=interaction, member=author
            )
            embed = Embed(
                title="You are not allowed to start multiple debates simultaneously.",
                description=f"Please wait till your existing debate in __Debate {debater_room.number}__ is finished.",
                color=0xF1C40F,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        if room.match.check_debater(author):
            embed = Embed(
                title="Command Disabled",
                description="You are already a debater.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        if not room.match.check_participant(author):
            embed = Embed(
                title="You must choose a position on the topic before "
                "you can debate.",
                description="`/for` - For the topic.\n\n"
                "`/against` - Against the topic.",
                color=0xF1C40F,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        current_session_start = datetime.utcnow()
        for participant in room.match.participants:
            participant.session_start = current_session_start

        room.match.add_debater(author)

        await author.edit(mute=False)

        debater_data = await self.bot.engine.find_one(
            MemberModel, MemberModel.member == interaction.user.id
        )
        debater_data.debate_count += 1
        await self.bot.engine.save(debater_data)

        embed = Embed(
            title="You are now a debater on the topic.",
            description="Your skill rating is at risk. Be mindful of what you say.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed)

    @app_commands.command(name="vote", description="Vote for you think won the debate")
    async def debate_vote(
        self, interaction: discord.Interaction, debater: Member
    ) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        author = interaction.user
        candidate = debater

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        if not room.check_match():
            await update(
                interaction,
                embed=Embed(
                    title="Command Disabled",
                    description="This command only works if a debate room has a current topic.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )

        if candidate == author:
            embed = Embed(
                title="Invalid Candidate",
                description="You cannot vote for yourself.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        candidate_debater = room.match.get_debater(candidate)

        if candidate_debater:
            if author in [candidate_debater.votes]:
                embed = Embed(
                    title="Vote Already Cast",
                    description="Your vote has been cast already.",
                    color=0xF1C40F,
                )
                await update(interaction, embed=embed, ephemeral=True)
                return
        else:
            embed = Embed(
                title="Invalid Candidate",
                description="You can only vote for debaters.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        await interaction.response.send_modal(
            DebateVotingRubric(
                states={
                    "room": room,
                    "author": author,
                    "candidate": candidate,
                }
            )
        )

    @app_commands.command(
        name="private", description="Convert a public debate into a private one."
    )
    @app_commands.checks.has_any_role(
        "The Crown", "Chancellor", "Liege", "Prime Minister", "Minister"
    )
    async def private(self, interaction: discord.Interaction) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )

        if room.private:
            embed = Embed(
                title="Room Private Already",
                description="This room is already private.",
                color=0xF1C40F,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        room.private = True

        for member in room.vc.members:
            await member.edit(mute=True)

        if room.match:
            room.match = None
        room.purge_topics()
        room.private_debaters = []

        await update_im(bot=self.bot, room_num=room.number)
        embed = Embed(
            title="Room Converted",
            description="This room is now private.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed)

    @app_commands.command(
        name="public", description="Convert a private debate into a public one."
    )
    @app_commands.checks.has_any_role(
        "The Crown", "Chancellor", "Liege", "Prime Minister", "Minister"
    )
    async def public(self, interaction: discord.Interaction) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )

        if room.private:
            room.private = False
        else:
            embed = Embed(
                title="Room Public Already",
                description="This room is already public.",
                color=0xF1C40F,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        for member in room.vc.members:
            await member.edit(mute=False)

        if room.match:
            room.match = None
        room.purge_topics()
        room.private_debaters = []

        await update_im(bot=self.bot, room_num=room.number)
        embed = Embed(
            title="Room Converted",
            description="This room is now public.",
            color=0x2ECC71,
        )
        await update(interaction, embed=embed)

    @app_commands.command(
        name="unlock",
        description="Unlock a member in a private room to allow them to debate or set topics.",
    )
    @app_commands.checks.has_any_role(
        "The Crown", "Chancellor", "Liege", "Prime Minister", "Minister"
    )
    async def unlock(
        self, interaction: discord.Interaction, participant: Member
    ) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        unlocked_member = participant

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )

        if not room.private:
            embed = Embed(
                title="Command Unauthorized",
                description="You can only unlock members in a private room.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        if unlocked_member in [_ for _ in room.private_debaters]:
            embed = Embed(
                title="Participant Already Unlocked",
                description="This member is already unlocked in this room.",
                color=0xF1C40F,
            )
            await update(interaction, embed=embed, ephemeral=True)
        else:
            if unlocked_member in room.vc.members:
                room.private_debaters.append(unlocked_member)
                if room.match:
                    await unlocked_member.edit(mute=True)
                else:
                    if room.current_topic:
                        await unlocked_member.edit(mute=False)

            embed = Embed(
                title="Participant Unlocked",
                description=f"{participant.mention} is now allowed to debate in the room.",
                color=0x2ECC71,
            )
            avatar_url = None
            if unlocked_member.avatar:
                avatar_url = unlocked_member.avatar.url
            embed.set_author(name=f"{unlocked_member.username}", icon_url=avatar_url)
            await update(interaction, embed=embed)

    @app_commands.command(
        name="conclude",
        description="Unlock a member in a private room to allow them to debate or set topics.",
    )
    async def conclude(self, interaction: discord.Interaction) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if not room.check_match():
            await update(
                interaction,
                embed=Embed(
                    title="Command Disabled",
                    description="This command only works if a debate room has a current topic.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )

        debaters, concluded, voters = room.vote_conclude(voter=interaction.user)
        if concluded is None:
            embed = Embed(
                title="Already Concluding",
                description="The debate is already concluding.",
                color=0xF1C40F,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return
        else:
            embed = Embed(
                title="Conclude Vote Cast",
                description="You have voted to conclude the debate.",
                color=0xEC6A5C,
            )
            await update(interaction, embed=embed)

        if concluded:
            room.match.concluding = True
            embed = Embed(
                title="Debate Concluding",
                description="Ratings are being updated. Debate specific commands will not run.",
                color=0xE67E22,
            )
            await room.vc.send(embed=embed)

            if room.match:
                for debater in debaters:
                    # Mute
                    if debater.member in room.vc.members:
                        await debater.member.edit(mute=True)
            else:
                if room.private:
                    for member in room.private_debaters:
                        await member.edit(mute=False)
                else:
                    for member in room.vc.members:
                        await member.edit(mute=False)

            if room.match:
                if room.match.check_voters():
                    for debater in debaters:
                        debater_rating = float(
                            20 * ((debater.mu_post - 3 * debater.sigma_post) + 25)
                        )
                        debater_data = await self.bot.engine.find_one(
                            MemberModel, MemberModel.member == debater.member.id
                        )
                        debater_data.mu = debater.mu_post
                        debater_data.sigma = debater.sigma_post
                        debater_data.rating = debater_rating

                        await self.bot.engine.save(debater_data)

                        avatar_url = None
                        if debater.member.avatar:
                            avatar_url = debater.member.avatar.url
                        embed = Embed(title="Rating Change", color=0xEC6A5C)
                        embed.set_footer(
                            text=debater.member.display_name,
                            icon_url=avatar_url,
                        )
                        embed.add_field(
                            name="Mean",
                            value=f"```diff\n"
                            f"- {float(debater.mu_pre): .2f}\n"
                            f"+ {float(debater.mu_post): .2f}\n"
                            f"```",
                            inline=True,
                        )
                        embed.add_field(
                            name="Confidence",
                            value=f"```diff\n"
                            f"- {float(debater.sigma_pre): .2f}\n"
                            f"+ {float(debater.sigma_post): .2f}\n"
                            f"```",
                            inline=True,
                        )
                        embed.add_field(
                            name="Rating",
                            value=f"```diff\n"
                            f"- {float(20 * ((debater.mu_pre - 3 * debater.sigma_pre) + 25)): .2f}\n"
                            f"+ {float(20 * ((debater.mu_post - 3 * debater.sigma_post) + 25)): .2f}\n"
                            f"```",
                            inline=True,
                        )

                        fifo: Queue = self.bot.state["debate_feed_fifo"]
                        fifo.put(embed)

                        # Update Roles
                        floored_rating = floor_rating(
                            float(
                                20 * ((debater.mu_post - 3 * debater.sigma_post) + 25)
                            )
                        )
                        rank_role: Optional[Role] = None
                        for rank, rating in RANK_RATING_MAP.items():
                            if math.isclose(floored_rating, rating, rel_tol=1e-04):
                                rank_role = self.bot.state["map_roles"][rank]
                                break

                        if rank_role not in debater.member.roles:
                            await debater.member.add_roles(
                                rank_role, reason="Added at the end of a debate match."
                            )

                        for rank, rating in RANK_RATING_MAP.items():
                            rank_role_id = self.bot.state["map_roles"][rank]
                            if rank_role_id in debater.member.roles:
                                if rank_role_id != rank_role:
                                    await debater.member.remove_roles(
                                        rank_role_id,
                                        reason="Removed at the end of a debate match.",
                                    )

                    embed = Embed(title="Voter Log", color=0xEC6A5C)
                    value = ""
                    debaters_by_votes = sorted(
                        room.match.get_debaters(), key=lambda d: d.votes
                    )
                    for debater in debaters_by_votes:
                        voters = sorted(debater.votes, key=lambda p: p.total_votes())
                        for voter in voters:
                            value += f"{voter.type()} {voter.member.mention} → {debater.type()} {debater.member.mention}\n"
                    embed.description = value
                    fifo: Queue = self.bot.state["debate_feed_fifo"]
                    fifo.put(embed)

            # Update topic
            current_topic = room.current_topic
            if current_topic:
                await update_im(
                    bot=self.bot,
                    room_num=get_room_number(bot=self.bot, channel=room.vc),
                )
                room.remove_topic(current_topic.author)
                room.vote_topic(current_topic.author, current_topic.author)
            else:
                await update_im(
                    bot=self.bot,
                    room_num=get_room_number(bot=self.bot, channel=room.vc),
                )

            room.updating_topic = True
            await update_topic(bot=self.bot, room=room)
            room.updating_topic = False

            # Clear private debaters
            room.private_debaters = []

            if room.match:
                check_voters = room.match.check_voters()
                room.match.concluding = False
                room.match.concluded = True
            else:
                check_voters = None

            # Remove voters from data set
            room.remove_conclude_voters()
            room.match = None  # Clear match

            embed = Embed(
                title="Debate Concluded",
                description="Ratings have been updated.",
                color=0x2ECC71,
            )
            if not check_voters:
                embed.description = (
                    "Ratings have not been updated due to lack of voters."
                )
            await room.vc.send(embed=embed)
        else:
            if not debaters:
                return
            if len(debaters) == 0:
                embed = Embed(
                    title="Conclude Failed",
                    description="You cannot conclude an empty debate room.",
                    color=0xE74C3C,
                )
                await update(interaction, embed=embed, ephemeral=True)

    @app_commands.command(
        name="consent",
        description="Consent to being recorded to speak in the room.",
    )
    async def consent(self, interaction: discord.Interaction) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        author = interaction.user

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        if room.match:
            if room.match.concluding:
                await update(
                    interaction,
                    embed=Embed(
                        title="Command Temporarily Disabled",
                        description="This command only works once the debate match has finished concluding.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )

        if room.studio:
            room.studio_participants.append(author)
            if room.match:
                if room.match.check_debater(member=author):
                    await author.edit(mute=False)
            else:
                await author.edit(mute=False)
            embed = Embed(
                title="Consent Received",
                description=f"{author.mention} has consented to being recorded.",
                color=0x2ECC71,
            )
            await update(interaction, embed=embed)
            return
        else:
            embed = Embed(
                title="Command Unauthorized",
                description=f"This is not a studio room.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

    @app_commands.command(
        name="proposition",
        description="Get a random proposition.",
    )
    async def proposition(self, interaction: discord.Interaction) -> None:
        embed = Embed(
            title="Random Proposition",
            description=f"{random.choice(self.bot.state['propositions']).strip()}",
        )
        await update(interaction, embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            # Do nothing if the message is persistent embed
            if len(message.embeds) > 0:
                if message.embeds[0].title.startswith("Debate Room"):
                    return

        if message.channel in [room.vc for room in self.bot.state["debate_rooms"]]:
            # Get number
            room_num = get_room_number(self.bot, message.channel)

            # Delete interface message
            index = room_num - 1
            im_del = self.bot.state["interface_messages"][index]
            try:
                im_del = await message.channel.fetch_message(im_del)
            except discord.errors.NotFound as e_info:
                im_del = None

            try:
                if im_del:
                    await im_del.delete()
            except discord.errors.NotFound as e_info:
                return

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if channel in [room.vc for room in self.bot.state["debate_rooms"]]:
            # Add interface message when embed is deleted
            if payload.message_id in self.bot.state["interface_messages"]:
                index = get_room_number(self.bot, channel) - 1
                if not self.bot.state["exiting"]:
                    im = await add_interface_message(self.bot, index)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        for message_id in payload.message_ids:
            if channel in [room.vc for room in self.bot.state["debate_rooms"]]:
                # Add interface message when embed is deleted
                if message_id in self.bot.state["interface_messages"]:
                    index = get_room_number(self.bot, channel) - 1
                    if not self.bot.state["exiting"]:
                        im = await add_interface_message(self.bot, index)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        if member.bot:
            await member.add_roles(self.bot.state["map_roles"]["role_bot"])
            return

        member_data = await self.bot.engine.find_one(
            MemberModel, MemberModel.member == member.id
        )
        if member_data:
            floored_rating = floor_rating(
                float(20 * ((member_data.mu - 3 * member_data.sigma) + 25))
            )
            current_rank_role: typing.Optional[Role] = None
            for rank, rating in RANK_RATING_MAP.items():
                if math.isclose(floored_rating, rating, rel_tol=1e-04):
                    current_rank_role = self.bot.state["map_roles"][rank]
                    break

            if current_rank_role not in member.roles:
                await member.add_roles(
                    current_rank_role, reason="Added during member join."
                )

            for rank, rating in RANK_RATING_MAP.items():
                rank_role = self.bot.state["map_roles"][rank]
                if rank_role in member.roles:
                    if rank_role != current_rank_role:
                        await member.remove_roles(
                            rank_role, reason="Removed during member join."
                        )
        else:
            member_data = MemberModel(member=member)
            await self.bot.engine.save(member_data)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        debate_rooms: typing.List[DebateRoom] = self.bot.state["debate_rooms"]
        roles = self.bot.state["map_roles"]
        checked_roles = [
            roles["role_chancellor"],
            roles["role_liege"],
            roles["role_prime_minister"],
            roles["role_minister"],
        ]

        # Do nothing if mute event
        if before.mute and not after.mute:
            return
        if not before.mute and after.mute:
            return

        if before.deaf and not after.deaf:
            return
        if not before.deaf and after.deaf:
            return

        if before.self_mute and not after.self_mute:
            return
        if not before.self_mute and after.self_mute:
            return

        if before.self_deaf and not after.self_deaf:
            return
        if not before.self_deaf and after.self_deaf:
            return

        if before.self_stream and not after.self_stream:
            return
        if not before.self_stream and after.self_stream:
            return

        if before.self_video and not after.self_video:
            return
        if not before.self_video and after.self_video:
            return

        async def join_room():
            after_vc = after.channel
            room_after_number = get_room_number(self.bot, after_vc)
            room_after = None
            if room_after_number:
                room_after = get_room(self.bot, room_after_number)
                room_after.add_topic_voter(member)
                room_after.reset_topic_creation(member)

                if room_after.match:
                    participant = room_after.match.get_participant(member)
                    if participant:
                        participant.session_start = datetime.utcnow()

                # Allow members to send messages in linked text chat
                await room_after.vc.set_permissions(member, send_messages=True)

                if room_after.match:
                    if room_after.match.check_debater(member):
                        if room_after.private:
                            if room_after.studio:
                                if (
                                    self.bot.state["map_roles"]["role_detained"]
                                    in member.roles
                                ):
                                    await member.edit(mute=True)
                                else:
                                    if member in room_after.private_debaters:
                                        if member in room_after.studio_participants:
                                            await member.edit(mute=False)
                                    else:
                                        if member not in room_after.studio_participants:
                                            await member.edit(mute=True)
                            else:
                                if (
                                    self.bot.state["map_roles"]["role_detained"]
                                    in member.roles
                                ):
                                    await member.edit(mute=True)
                                else:
                                    if member in room_after.private_debaters:
                                        await member.edit(mute=False)
                                    else:
                                        await member.edit(mute=True)
                        else:
                            if room_after.studio:
                                if (
                                    self.bot.state["map_roles"]["role_detained"]
                                    in member.roles
                                ):
                                    await member.edit(mute=True)
                                else:
                                    if member in room_after.studio_participants:
                                        await member.edit(mute=False)
                            else:
                                if (
                                    self.bot.state["map_roles"]["role_detained"]
                                    in member.roles
                                ):
                                    await member.edit(mute=True)
                                else:
                                    await member.edit(mute=False)
                    else:
                        if room_after.studio:
                            if member not in room_after.studio_participants:
                                await member.edit(mute=True)
                        else:
                            await member.edit(mute=True)
                else:
                    if room_after.private:
                        if room_after.studio:
                            if (
                                self.bot.state["map_roles"]["role_detained"]
                                in member.roles
                            ):
                                await member.edit(mute=True)
                            else:
                                if member in room_after.private_debaters:
                                    if member in room_after.studio_participants:
                                        await member.edit(mute=False)
                                    else:
                                        await member.edit(mute=True)
                                else:
                                    if member in room_after.studio_participants:
                                        await member.edit(mute=False)
                                    else:
                                        await member.edit(mute=True)
                        else:
                            if (
                                self.bot.state["map_roles"]["role_detained"]
                                in member.roles
                            ):
                                await member.edit(mute=True)
                            else:
                                if member in room_after.private_debaters:
                                    await member.edit(mute=False)
                                else:
                                    await member.edit(mute=True)
                    else:
                        if room_after.studio:
                            if (
                                self.bot.state["map_roles"]["role_detained"]
                                in member.roles
                            ):
                                await member.edit(mute=True)
                            else:
                                if member in room_after.studio_participants:
                                    await member.edit(mute=False)
                                else:
                                    await member.edit(mute=True)
                        else:
                            if (
                                self.bot.state["map_roles"]["role_detained"]
                                in member.roles
                            ):
                                await member.edit(mute=True)
                            else:
                                await member.edit(mute=False)

        async def leave_room():
            before_vc = before.channel
            room_before_number = get_room_number(self.bot, before_vc)
            room_before = get_room(self.bot, room_before_number)
            if room_before_number:
                room_before = get_room(self.bot, room_before_number)
                room_before.remove_topic_voter(member)
                room_before.remove_priority_from_topic(member)

                active_debaters = []
                if room_before.match:
                    participant = room_before.match.get_participant(member)
                    if participant:
                        participant.session_end = datetime.utcnow()
                        participant.update_duration()

                    debaters = [d.member for d in room_before.match.get_debaters()]

                    for voice_member in before_vc.members:
                        if voice_member in debaters:
                            active_debaters.append(voice_member)

                if room_before:
                    await room_before.vc.set_permissions(member, overwrite=None)

                    # Remove Recording Session
                    try:
                        if member == room_before.studio_engineer:
                            await asyncio.wait_for(asyncio.sleep(180), timeout=120)
                    except asyncio.TimeoutError:
                        room_before.studio = False
                        room_before.studio_engineer = None
                        await update_im(bot=self.bot, room_num=room_before.number)

                    # Delete if not working
                    room_before.updating_topic = True
                    await update_topic(self.bot, room_before)
                    room_before.updating_topic = False

        if before.channel is None and after.channel:
            if before.channel is None and after.channel in [
                room.vc for room in debate_rooms
            ]:
                await join_room()
                return

        if before.channel and after.channel is None:
            if (
                before.channel in [room.vc for room in debate_rooms]
                and after.channel is None
            ):
                await leave_room()
                return

        after_list = []
        if after.channel:
            after_list = list([room.vc for room in debate_rooms])
            if after.channel in after_list:
                after_list.remove(after.channel)
        else:
            return

        before_list = []
        if before.channel:
            before_list = list([room.vc for room in debate_rooms])
            if before.channel in before_list:
                before_list.remove(before.channel)
        else:
            return

        if before.channel and after.channel and after_list and before_list:
            if before.channel not in after_list and after.channel in before_list:
                await join_room()
                await leave_room()
                return
            elif before.channel in after_list and after.channel not in before_list:
                await join_room()
                await leave_room()
                return
            elif before.channel in after_list and after.channel in before_list:
                await join_room()
                await leave_room()


@app_commands.default_permissions(send_messages=True)
class Studio(
    commands.GroupCog,
    name="studio",
    description="Control the recording status of a debate room.",
):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_error(self, interaction: Interaction, error: AppCommandError):
        if isinstance(error, MissingAnyRole):
            await update(
                interaction,
                embed=Embed(
                    title="Command Unauthorized",
                    description="You are not authorized to run this command.",
                    color=0xE74C3C,
                ),
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
            )
            return

    @app_commands.command(
        name="start",
        description="Start a recording session.",
    )
    async def start(self, interaction: discord.Interaction) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        author = interaction.user

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        if room.check_match():
            await update(
                interaction,
                embed=Embed(
                    title="Command Unauthorized",
                    description=f"You can only claim a room without an existing match.",
                    color=0xE74C3C,
                ),
            )
            return

        if room.studio:
            embed = Embed(
                title="Command Unauthorized",
                description=f"This room is already claimed by f{room.studio_engineer.mention}.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return
        else:
            room.studio = True
            room.studio_engineer = author

            await interaction.response.defer()

            for member in room.vc.members:
                await member.edit(mute=True)

            await update_im(bot=self.bot, room_num=room.number)

            embed = Embed(
                title="Studio Initialized",
                description="This room is potentially being recorded.",
                color=0x2ECC71,
            )
            await update(interaction, embed=embed)
            return

    @app_commands.command(
        name="stop",
        description="Stop a recording session.",
    )
    async def stop(self, interaction: discord.Interaction) -> None:
        # These checks handle error messages automatically.
        if not await in_debate_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        author = interaction.user

        if room.updating_topic:
            await update(
                interaction,
                embed=Embed(
                    title="Command Temporarily Disabled",
                    description="This command only works once the topic has finished updating.",
                    color=0xE74C3C,
                ),
                errored=True,
                ephemeral=True,
            )
            return

        if not room.studio:
            embed = Embed(
                title="Command Unauthorized",
                description=f"This is not a studio room.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return
        else:
            if author != room.studio_engineer:
                embed = Embed(
                    title="Command Unauthorized",
                    description=f"Only the studio engineer can run this command.",
                    color=0xE74C3C,
                )
                await update(interaction, embed=embed, ephemeral=True)
                return

            await interaction.response.defer()

            room.studio = False
            room.studio_engineer = None

            if not room.match:
                for member in room.vc.members:
                    await member.edit(mute=False)

            await update_im(bot=self.bot, room_num=room.number)

            embed = Embed(
                title="Studio Ended",
                description="No one is allowed to record in this room anymore.",
                color=0x2ECC71,
            )
            await update(interaction, embed=embed)
            return


async def setup(bot: ArgusClient) -> None:
    await bot.add_cog(
        Skill(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
    await bot.add_cog(
        Topic(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
    await bot.add_cog(
        Debate(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
    await bot.add_cog(
        Studio(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
