import typing
from datetime import datetime
from typing import Optional

import discord
import openskill
import pymongo
from discord import app_commands, Member, Interaction, Embed
from discord.ext import commands

from argus.client import ArgusClient
from argus.common import (
    insert_skill,
    get_room_number,
    in_debate_room,
    unlocked_in_private_room,
    get_room,
    update_im,
    update_topic,
)
from argus.models import DebateRoom, DebateTopic, DebateParticipant
from argus.utils import update


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
                rank = interaction.guild.get_role(current_rank_role)

                embed = Embed(title="Skill Rating", color=0xEC6A5C)
                embed.set_footer(text=member.display_name, icon_url=member.avatar.url)
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
                embed.add_field(name="Title", value=f"{rank.mention}", inline=True)
                await update(interaction, embed=embed, ephemeral=True)
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
            member_doc = self.bot.db[self.bot.db.database].MemberModel.aggregate(
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
            rank = interaction.guild.get_role(current_rank_role)

            embed = Embed(title="Skill Rating", color=0xEC6A5C)
            embed.set_footer(
                text=interaction.user.display_name, icon_url=interaction.user.avatar.url
            )
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
            embed.add_field(name="Title", value=f"{rank.mention}", inline=True)
            await update(interaction, embed=embed, ephemeral=True)

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
        if not in_debate_room(self.bot, interaction):
            return
        if not unlocked_in_private_room(self.bot, interaction):
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

        await update_im(self.bot, interaction, room_num=room.number)

        room.updating_topic = True
        await update_topic(self.bot, interaction, room)
        room.updating_topic = False

    @app_commands.command(
        name="vote",
        description="Vote for who's topic you want to be debated.",
    )
    async def vote(self, interaction: Interaction, debater: Member) -> None:
        if debater.bot:
            embed = Embed(
                title="Invalid User",
                description="You cannot vote for bots.",
                color=0xE74C3C,
            )
            await update(interaction, embed=embed, ephemeral=True)
            return

        # These checks handle error messages automatically.
        if not in_debate_room(self.bot, interaction):
            return
        if not unlocked_in_private_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        candidate = debater

        if not room.check_match():
            await update(
                interaction,
                embed=Embed(
                    title="Command Disabled",
                    description="This command only works if a debate match is ongoing.",
                    color=0xE74C3C,
                ),
            )
            return

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
        await update_topic(self.bot, interaction, room)
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
        if not in_debate_room(self.bot, interaction):
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
            if member.id == topic.author.id:
                embed = Embed(
                    title="Member Topic",
                    color=0xEC6A5C,
                )
                if topic.prioritized:
                    embed.add_field(name="Topic [Prioritized]", value=f"{str(topic)}")
                else:
                    embed.add_field(name="Topic", value=f"{str(topic)}")
                embed.add_field(name="Votes", value=f"{str(topic.votes)}")
                embed.set_footer(
                    text=f"{member.display_name}", icon_url=member.avatar.url
                )
                await update(interaction, embed=embed, ephemeral=True)
                return

        embed = Embed(
            title="Topic Author Not Found",
            description="No topic was authored by the given user.",
            color=0xE74C3C,
        )
        await update(interaction, embed=embed, ephemeral=True)

    @app_commands.command(
        name="view",
        description="View user's topic and it's details.",
    )
    @app_commands.checks.has_any_role(
        "The Crown", "Chancellor", "Liege", "Prime Minister", "Minister"
    )
    async def remove(
        self, interaction: Interaction, member: Optional[Member] = None
    ) -> None:

        # These checks handle error messages automatically.
        if not in_debate_room(self.bot, interaction):
            return
        if not unlocked_in_private_room(self.bot, interaction):
            return

        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)

        if not room.check_match():
            await update(
                interaction,
                embed=Embed(
                    title="Command Disabled",
                    description="This command only works if a debate match is ongoing.",
                    color=0xE74C3C,
                ),
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
        await update_topic(self.bot, interaction, room)

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

    @app_commands.command(name="for")
    async def stance_for(self, interaction: discord.Interaction) -> None:
        channel = interaction.channel
        room_number = get_room_number(self.bot, channel)
        room: typing.Optional[DebateRoom] = get_room(self.bot, room_number)
        author = interaction.user

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
