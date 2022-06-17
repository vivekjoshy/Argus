import math
import typing
from queue import Queue
from typing import Optional, List

import discord
from discord import Embed, VoiceChannel, Interaction, Member, Role

from argus.client import ArgusClient
from argus.constants import DB_ROLE_NAME_MAP, RANK_RATING_MAP
from argus.db.models.guild import GuildModel
from argus.db.models.user import MemberModel
from argus.models import DebateRoom
from argus.utils import update, floor_rating


def get_room_number(bot: ArgusClient, channel: VoiceChannel) -> Optional[int]:
    """Get a room number from a TextChannel or VoiceChannel ID."""
    debate_rooms: List[DebateRoom] = bot.state["debate_rooms"]
    for room in debate_rooms:
        if channel.id == room.vc.id:
            return room.number
    else:
        return None


def get_room(bot: ArgusClient, room_num: int) -> Optional[DebateRoom]:
    """Get a room from a room number."""
    debate_rooms = bot.state["debate_rooms"]
    try:
        room = list(filter(lambda x: x.number == room_num, debate_rooms))[0]
        return room
    except IndexError as e_info:
        return None


def get_embed_message(room_num):
    response = Embed(
        colour=0xEB6A5C,
        title=f"Debate Room {room_num}",
        description="Set room topics democratically and vote for "
        "the best debater. Make sure to set your stance as soon as "
        "possible to ensure your vote counts more.",
    )
    return response


async def send_embed_message(
    bot: ArgusClient, room_num: int, embed: Optional[Embed] = None
):
    if embed:
        debate_rooms = bot.state["debate_rooms"]
        voice_channel: VoiceChannel = debate_rooms[room_num - 1].vc
        message = await voice_channel.send(embed=embed)
        return message

    embed = get_embed_message(room_num=room_num)
    room = get_room(bot, room_num)
    if room.studio:
        embed.title = f"{embed.title} [Recording]"
        embed.add_field(name="Studio Engineer", value=f"{room.studio_engineer.mention}")

    topic_updated = get_room(bot, room_num).set_current_topic()
    current_topic = get_room(bot, room_num).current_topic
    if current_topic:
        embed.add_field(name="Current Topic: ", value=f"{current_topic}")

    debate_rooms = bot.state["debate_rooms"]
    voice_channel: VoiceChannel = debate_rooms[room_num - 1].vc
    message = await voice_channel.send(embed=embed)
    return message


async def check_roles_exist(bot: ArgusClient, interaction: Interaction) -> bool:
    guild = bot.get_guild(bot.config["global"]["guild_id"])

    # Setup Role Cache
    for role in guild.roles:
        if not role.managed:
            bot.state["map_roles"][DB_ROLE_NAME_MAP[role.name]] = role

    # Check Roles Exist in Database
    db_guilds = await bot.engine.find(GuildModel)
    db_roles = db_guilds[0].roles

    for role in guild.roles[1:]:
        if not role.managed:
            db_role_id = interaction.guild.get_role(
                db_roles[DB_ROLE_NAME_MAP[role.name]]
            ).id
            if not db_role_id:
                await update(
                    interaction,
                    embed=Embed(
                        title=f"Roles Missing",
                        description="Please run the setup of roles again. "
                        "Roles in the database are missing from the server.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return False
            elif role.id == db_role_id:
                continue
            else:
                await update(
                    interaction,
                    embed=Embed(
                        title=f"Data Mismatch",
                        description="Please run the setup of roles again. "
                        "Roles in the server do not match the database.",
                        color=0xE74C3C,
                    ),
                    ephemeral=True,
                )
                return False
    return True


def check_level_2(
    bot: ArgusClient,
    interaction: Interaction,
) -> bool:
    if interaction.guild.premium_tier >= 2:
        return True


async def insert_skill(
    bot: ArgusClient, interaction: Interaction, member: Member
) -> dict:
    """
    Initializes member's skill if it doesn't already in database. Also updates their roles.
    """
    role_member = discord.utils.get(interaction.guild.roles, name="Member")
    role_citizen = discord.utils.get(interaction.guild.roles, name="Citizen")
    member_data: Optional[MemberModel] = await bot.engine.find_one(
        MemberModel, MemberModel.member == member.id
    )
    if member_data:
        if not member_data.mu or not member_data.sigma or not member_data.rating:
            mu = 25.0
            sigma = 25 / 3
            rating = float(20 * ((mu - 3 * sigma) + 25))

            if (
                member_data.citizenship_revoked is None
                or member_data.citizenship_revoked is False
            ):
                member_data.citizenship_revoked = False
            else:
                member_data.citizenship_revoked = True

            if (
                member_data.membership_revoked is None
                or member_data.membership_revoked is False
            ):
                member_data.membership_revoked = False
            else:
                member_data.membership_revoked = True

            if member_data.citizenship_revoked:
                await member.remove_roles(
                    role_citizen, reason="Citizenship status repaired."
                )
            if member_data.membership_revoked:
                await member.remove_roles(
                    role_member, reason="Membership status repaired."
                )

            member_data.mu = mu
            member_data.sigma = sigma
            member_data.rating = rating

            await bot.engine.save(member_data)

            floored_rating = floor_rating(float(20 * ((mu - 3 * sigma) + 25)))
            current_rank_role: typing.Optional[Role] = None
            for rank, rating in RANK_RATING_MAP.items():
                if math.isclose(floored_rating, rating, rel_tol=1e-04):
                    current_rank_role = bot.state["map_roles"][rank]
                    break

            if current_rank_role not in member.roles:
                await member.add_roles(
                    current_rank_role, reason="Added during skill view."
                )

            for rank, rating in RANK_RATING_MAP.items():
                rank_role = bot.state["map_roles"][rank]
                if rank_role in member.roles:
                    if rank_role != current_rank_role:
                        await member.remove_roles(
                            rank_role, reason="Removed during skill view."
                        )
            return {
                "mu": mu,
                "sigma": sigma,
                "rating": rating,
                "current_rank_role": current_rank_role,
            }
        else:
            mu = member_data.mu
            sigma = member_data.sigma
            rating = member_data.rating

            floored_rating = floor_rating(float(rating))
            current_rank_role: typing.Optional[Role] = None
            for rank, rating in RANK_RATING_MAP.items():
                if math.isclose(floored_rating, rating, rel_tol=1e-04):
                    current_rank_role = bot.state["map_roles"][rank]
                    break

            if current_rank_role not in member.roles:
                await member.add_roles(
                    current_rank_role, reason="Added during skill view."
                )

            for rank, rating in RANK_RATING_MAP.items():
                rank_role = bot.state["map_roles"][rank]
                if rank_role in member.roles:
                    if rank_role != current_rank_role:
                        await member.remove_roles(
                            rank_role, reason="Removed during skill view."
                        )

            return {
                "mu": mu,
                "sigma": sigma,
                "rating": rating,
                "current_rank_role": current_rank_role,
            }

    else:
        member_data = MemberModel(member=member)

        mu = 25.0
        sigma = 25 / 3
        rating = float(20 * ((mu - 3 * sigma) + 25))

        member_data.mu = mu
        member_data.sigma = sigma
        member_data.rating = rating

        await bot.engine.save(member_data)

        floored_rating = floor_rating(float(20 * ((mu - 3 * sigma) + 25)))
        current_rank_role: typing.Optional[Role] = None
        for rank, rating in RANK_RATING_MAP.items():
            if math.isclose(floored_rating, rating, rel_tol=1e-04):
                current_rank_role = bot.state["map_roles"][rank]
                break

        if current_rank_role not in member.roles:
            await member.add_roles(current_rank_role, reason="Added during skill view.")

        for rank, rating in RANK_RATING_MAP.items():
            rank_role = bot.state["map_roles"][rank]
            if rank_role in member.roles:
                if rank_role != current_rank_role:
                    await member.remove_roles(
                        rank_role, reason="Removed during skill view."
                    )
        return {
            "mu": mu,
            "sigma": sigma,
            "rating": rating,
            "current_rank_role": current_rank_role,
        }


async def in_debate_room(bot: ArgusClient, interaction: Interaction) -> bool:
    """
    Checks if the command is run while in a debate room.
    """
    channel = interaction.channel
    if not isinstance(channel, VoiceChannel):
        await update(
            interaction,
            embed=Embed(
                title="Incorrect Channel",
                description="This command cannot be run in this channel.",
                color=0xE74C3C,
            ),
            ephemeral=True,
        )
        return False

    room_number = get_room_number(bot, channel)
    if not room_number:
        await update(
            interaction,
            embed=Embed(
                title="Incorrect Channel",
                description="This command cannot be run in this channel.",
                color=0xE74C3C,
            ),
            ephemeral=True,
        )
        return False

    author = interaction.user
    if author in channel.members:
        return True

    await update(
        interaction,
        embed=Embed(
            title="Incorrect Channel",
            description="This command requires you to be in the accompanying debate voice channel.",
            color=0xE74C3C,
        ),
        ephemeral=True,
    )
    return False


async def unlocked_in_private_room(bot: ArgusClient, interaction: Interaction) -> bool:
    """
    Checks if the command is run by a member unlocked in the
    corresponding private room.
    """
    channel = interaction.channel
    channel = interaction.channel
    if not isinstance(channel, VoiceChannel):
        await update(
            interaction,
            embed=Embed(
                title="Incorrect Channel",
                description="This command cannot be run in this channel.",
                color=0xE74C3C,
            ),
            ephemeral=True,
        )
        return False

    room_number = get_room_number(bot, channel)
    room: Optional[DebateRoom] = get_room(bot, room_number)

    if not room:
        await update(
            interaction,
            embed=Embed(
                title="Incorrect Channel",
                description="This command cannot be run in this channel.",
                color=0xE74C3C,
            ),
            ephemeral=True,
        )
        return False

    if not room.private:
        return True

    if interaction.user not in room.private_debaters:
        await update(
            interaction,
            embed=Embed(
                title="Unauthorized",
                description="Ask a moderator to unlock you in this room to run this command.",
                color=0xE74C3C,
            ),
            ephemeral=True,
        )
    return True


async def update_im(bot: ArgusClient, room_num: int):
    index = room_num - 1
    interface_messages = bot.state["interface_messages"]
    im_id = interface_messages[index]
    room = get_room(bot, room_num)

    embed = get_embed_message(room_num)

    try:
        im = await room.vc.fetch_message(im_id)
    except discord.errors.NotFound as e_info:
        im = None

    if room.studio:
        embed.title = f"{embed.title} [Recording]"
        embed.add_field(name="Studio Engineer", value=f"{room.studio_engineer.mention}")

    topic = room.current_topic
    if topic:
        embed.add_field(
            name="**Topic**: ",
            value=f"{get_room(bot, room_num).current_topic}",
        )
    try:
        if im:
            await im.edit(embed=embed)
    except discord.errors.NotFound as e_info:
        return


async def conclude_debate(
    bot: ArgusClient, interaction: Interaction, room: DebateRoom, debaters
):
    channels = bot.state["map_channels"]

    embed = Embed(
        title="Debate Concluding",
        description="Ratings are being updated. Debate specific commands will not run.",
        color=0xE67E22,
    )

    if room.match:
        check_voters = room.match.check_voters()
        if not check_voters:
            debaters = []
    else:
        check_voters = None
        debaters = []
        for member in room.vc.members:
            await member.edit(mute=False)

    if debaters:
        await interaction.channel.send(room.vc, embed=embed)

        for debater in debaters:
            # Mute
            if debater.member in room.vc.members:
                await debater.member.edit(mute=True)

        for debater in debaters:
            await room.vc.set_permissions(debater.member, overwrite=None)

    if len(debaters) > 1:
        for debater in debaters:
            debater_rating = float(
                20 * ((debater.mu_post - 3 * debater.sigma_post) + 25)
            )
            debater_data: Optional[MemberModel] = await bot.engine.find_one(
                MemberModel, MemberModel.member == debater.member.id
            )
            debater_data.mu = debater.mu_post
            debater_data.sigma = debater.sigma_post
            debater_data.rating = debater_rating

            await bot.engine.save(debater_data)

            embed = Embed(title="Rating Change", color=0xEC6A5C)
            embed.set_footer(
                text=debater.member.display_name, icon_url=debater.member.avatar.url
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

            fifo: Queue = bot.state["debate_feed_fifo"]
            fifo.put(embed)

            # Update Roles
            floored_rating = floor_rating(
                float(20 * ((debater.mu_post - 3 * debater.sigma_post) + 25))
            )
            rank_role: Optional[Role] = None
            for rank, rating in RANK_RATING_MAP.items():
                if math.isclose(floored_rating, rating, rel_tol=1e-04):
                    rank_role = bot.state["map_roles"][rank]
                    break

            if rank_role.id not in debater.member.role_ids:
                await debater.member.add_role(
                    rank_role, reason="Added at the end of a debate match."
                )

            for rank, rating in RANK_RATING_MAP.items():
                rank_role_id = bot.state["map_roles"][rank]
                if int(rank_role_id) in debater.member.role_ids:
                    if int(rank_role_id) != int(rank_role.id):
                        await debater.member.remove_role(
                            rank_role_id, reason="Removed at the end of a debate match."
                        )

        embed = Embed(title="Voter Log", color=0xEC6A5C)
        value = ""
        debaters_by_votes = sorted(room.match.get_debaters(), key=lambda d: d.votes)
        for debater in debaters_by_votes:
            voters = sorted(debater.votes, key=lambda p: p.total_votes())
            for voter in voters:
                value += f"{voter.type()} {voter.member.mention} → {debater.type()} {debater.member.mention}\n"
        embed.description = value
        fifo: Queue = bot.state["debate_feed_fifo"]
        fifo.put(embed)

    # Clear private debaters
    room.private_debaters = []

    embed = Embed(
        title="Debate Concluded.",
        description="Ratings have been updated.",
        color=0x2ECC71,
    )
    if not check_voters:
        embed.description = "Ratings have not been updated due to lack of voters."
    elif len(debaters) < 2:
        embed.description = "Ratings have not been updated due to lack of debaters."

    room.match = None  # Clear match

    if debaters:
        await room.vc.send(embed=embed)


async def update_topic(bot: ArgusClient, room: DebateRoom):
    """Update topic of room from current topic."""
    room.remove_obsolete_topics()

    if len(room.vc.members) == 0:
        current_topic = None
        topic_updated = False
    else:
        topic_updated = room.set_current_topic()
        current_topic = room.current_topic

    match = room.match

    if current_topic:
        if not match:
            topic_updated = room.set_current_topic()
            current_topic = room.current_topic
            room.start_match(current_topic)

            for member in room.vc.members:
                await room.vc.set_permissions(member, overwrite=None)
                await member.edit(mute=True)
            await update_im(bot, room.number)
        else:
            # Do nothing if there are no voters
            if not room.match.check_voters():
                debaters = room.match.get_debaters()

                if not topic_updated:
                    return

                # Mute debaters early
                for debater in debaters:
                    # Remove overwrite from VC and mute
                    await room.vc.set_permissions(debater.member, overwrite=None)
                    if debater.member in room.vc.members:
                        await debater.member.edit(mute=True)

            debaters = []
            if match.concluding is False and match.concluded is False:
                if topic_updated:

                    debaters = room.stop_match()

                    # Mute debaters early
                    for debater in debaters:
                        # Remove overwrite from VC and mute
                        await room.vc.set_permissions(debater.member, overwrite=None)
                        if debater.member in room.vc.members:
                            await debater.member.edit(mute=True)

                    match.concluding = True
                    await conclude_debate(bot, room, debaters)
                    match.concluding = False
                    match.concluded = True

                    topic_updated = room.set_current_topic()
                    current_topic = room.current_topic
                    room.start_match(current_topic)

                    await update_im(bot, room.number)
                    for member in room.vc.members:
                        await member.edit(mute=True)
            elif match.concluding is False and match.concluded is True:
                topic_updated = room.set_current_topic()
                current_topic = room.current_topic
                await update_im(bot, room.number)
                return
            elif match.concluding is True and match.concluded is False:
                topic_updated = room.set_current_topic()
                current_topic = room.current_topic
                await update_im(bot, room.number)
                return
    else:
        if match:
            if match.concluding is False and match.concluded is False:
                debaters = room.stop_match()

                # Mute debaters early
                for debater in debaters:
                    # Remove overwrite from VC and mute
                    await room.vc.set_permissions(debater.member, overwrite=None)
                    if debater.member in room.vc.members:
                        await debater.member.edit(mute=True)

                match.concluding = True
                await conclude_debate(bot, room, debaters)
                match.concluding = False
                match.concluded = True
                for member in room.vc.members:
                    await member.edit(mute=True)

        if room.private:
            for member in room.private_debaters:
                await member.edit(mute=False)
        else:
            for member in room.vc.members:
                await member.edit(mute=False)

    topic_updated = room.set_current_topic()
    current_topic = room.current_topic
    await update_im(bot, room.number)


def check_debater_in_any_room(
    bot: ArgusClient, interaction: Interaction, room, member: Member
) -> bool:
    """Ensure member is a debater in only one room."""
    rooms = list(bot.state["debate_rooms"])
    rooms.remove(room)
    for room in rooms:
        if room.match:
            if room.match.check_debater(member):
                return True
    return False


def get_debater_room(
    bot: ArgusClient, interaction: Interaction, member: Member
) -> Optional[DebateRoom]:
    """Get a room from a debater."""
    for room in bot.state["debate_rooms"]:
        if room.match:
            if room.match.check_debater(member):
                return room
    return None


async def consented(bot: ArgusClient, interaction: Interaction) -> bool:
    """
    Checks if the command is run by a member who consented in a studio
    room.
    """
    channel = interaction.channel
    room_number = get_room_number(bot, channel)
    room: Optional[DebateRoom] = get_room(bot, room_number)

    if not room:
        await update(
            interaction,
            embed=Embed(
                title="Incorrect Channel",
                description="This command cannot be run in this channel.",
                color=0xE74C3C,
            ),
            ephemeral=True,
        )
        return False

    if room.studio:
        if interaction.user not in room.studio_participants:
            await update(
                interaction,
                embed=Embed(
                    title="Unauthorized",
                    description="You need to consent to being recorded to use this command.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return False
    return True


async def add_interface_message(bot: ArgusClient, index, embed: Optional[Embed] = None):
    room_num = index + 1
    im_add = await send_embed_message(bot, room_num, embed)
    bot.state["interface_messages"][index] = im_add.id
    return bot.state["interface_messages"][index]
