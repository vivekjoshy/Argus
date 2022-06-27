import asyncio

import discord
from discord import app_commands, Embed, Permissions
from discord.ext import commands

from argus.checks import check_prerequisites_enabled
from argus.client import ArgusClient
from argus.common import check_roles_exist, check_level_2
from argus.constants import (
    DB_ROLE_NAME_MAP,
    ROLE_PERMISSIONS,
    RANK_RATING_MAP,
    ROLE_COLORS,
    DB_CHANNEL_NAME_MAP,
    CHANNEL_SORT_ORDER,
)
from argus.db.models.guild import GuildModel
from argus.overwrites import generate_overwrites, NEGATIVE, MODERATION_BOT, BASE
from argus.utils import update


@app_commands.default_permissions(administrator=True)
class Setup(commands.GroupCog, name="setup"):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot
        super().__init__()

        # Setup Roles
        self.bot.state["map_roles"] = {
            "role_warden": None,
            "role_the_crown": None,
            "role_moderation_bot": None,
            "role_chancellor": None,
            "role_liege": None,
            "role_prime_minister": None,
            "role_minister": None,
            "role_host": None,
            "role_grandmaster": None,
            "role_legend": None,
            "role_master": None,
            "role_expert": None,
            "role_distinguished": None,
            "role_apprentice": None,
            "role_novice": None,
            "role_initiate": None,
            "role_rookie": None,
            "role_incompetent": None,
            "role_bot": None,
            "role_judge": None,
            "role_server_booster": None,
            "role_citizen": None,
            "role_member": None,
            "role_promoter": None,
            "role_events": None,
            "role_logs": None,
            "role_debate_ping": None,
            "role_detained": None,
            "role_everyone": None,
        }

        # Setup Channels
        self.bot.state["map_channels"] = {
            "category_information": None,
            "tc_rules": None,
            "tc_about": None,
            "tc_announcements": None,
            "tc_community_updates": None,
            "category_moderation": None,
            "tc_mod_commands": None,
            "tc_isolation": None,
            "category_interface": None,
            "tc_election_feed": None,
            "tc_debate_feed": None,
            "tc_motions": None,
            "tc_commands": None,
            "category_events": None,
            "category_community": None,
            "tc_general": None,
            "tc_memes": None,
            "category_parliament": None,
            "vc_house_of_lords": None,
            "vc_house_of_commons": None,
            "category_debate": None,
            "category_logs": None,
            "tc_moderator_actions": None,
            "tc_message_deletion": None,
            "tc_message_edits": None,
            "tc_ban_unban": None,
            "tc_nicknames": None,
            "tc_join_leave": None,
            "tc_automod": None,
            "tc_channels": None,
            "tc_invites": None,
            "tc_roles": None,
            "tc_voice": None,
        }

    @app_commands.command(
        name="roles",
        description="Setup roles required by the bot. This is a dangerous procedure that alters the database.",
    )
    @check_prerequisites_enabled()
    async def roles(self, interaction: discord.Interaction) -> None:
        await update(
            interaction,
            embed=Embed(
                title="Processing Roles",
                description="This may take a while.",
                color=0xF1C40F,
            ),
        )

        if self.bot.state["roles_are_setup"]:
            await update(
                interaction,
                embed=Embed(
                    title="Roles Already Set Up",
                    description="Please restart the bot manually if your still want to overwrite roles.",
                    color=0xE74C3C,
                ),
            )
            return

        # Delete All Roles
        for role in list(interaction.guild.roles)[1:]:
            if not role.managed:
                await role.delete(reason="Role Setup")
                await asyncio.sleep(5)

        # Ease of Access
        roles = self.bot.state["map_roles"]

        # Setup Basic Permissions
        roles["role_everyone"] = interaction.guild.default_role
        await roles["role_everyone"].edit(
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_everyone"])
        )

        # Setup Power Roles
        roles["role_warden"] = await interaction.guild.create_role(
            name="Warden",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_warden"]),
            colour=0xEB6A5C,
            hoist=False,
        )
        await interaction.guild.me.add_roles(roles["role_warden"])

        roles["role_the_crown"] = await interaction.guild.create_role(
            name="The Crown",
            colour=0xD4AF37,
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_the_crown"]),
            hoist=False,
        )
        await interaction.guild.owner.add_roles(roles["role_the_crown"])

        roles["role_moderation_bot"] = await interaction.guild.create_role(
            name="Moderation Bot",
            permissions=Permissions(
                permissions=ROLE_PERMISSIONS["role_moderation_bot"]
            ),
            hoist=False,
        )

        roles["role_chancellor"] = await interaction.guild.create_role(
            name="Chancellor",
            colour=0x9B59B6,
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_chancellor"]),
            hoist=False,
        )

        roles["role_liege"] = await interaction.guild.create_role(
            name="Liege",
            colour=0xE67E22,
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_liege"]),
            hoist=False,
        )

        roles["role_prime_minister"] = await interaction.guild.create_role(
            name="Prime Minister",
            colour=0xE74C3C,
            permissions=Permissions(
                permissions=ROLE_PERMISSIONS["role_prime_minister"]
            ),
            hoist=False,
        )

        roles["role_minister"] = await interaction.guild.create_role(
            name="Minister",
            colour=0x2ECC71,
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_minister"]),
            hoist=False,
        )

        # Selective Permissions
        roles["role_host"] = await interaction.guild.create_role(
            name="Host",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_host"]),
            hoist=False,
        )

        # Event Roles
        roles["role_champion"] = await interaction.guild.create_role(
            name="Champion",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_champion"]),
            hoist=True,
        )

        # Setup Rated Roles
        roles["role_grandmaster"] = await interaction.guild.create_role(
            name="Grandmaster",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_grandmaster"]),
            hoist=True,
        )

        roles["role_legend"] = await interaction.guild.create_role(
            name="Legend",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_legend"]),
            hoist=True,
        )

        roles["role_master"] = await interaction.guild.create_role(
            name="Master",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_master"]),
            hoist=True,
        )

        roles["role_expert"] = await interaction.guild.create_role(
            name="Expert",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_expert"]),
            hoist=True,
        )

        roles["role_distinguished"] = await interaction.guild.create_role(
            name="Distinguished",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_distinguished"]),
            hoist=True,
        )

        roles["role_apprentice"] = await interaction.guild.create_role(
            name="Apprentice",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_apprentice"]),
            hoist=True,
        )

        roles["role_novice"] = await interaction.guild.create_role(
            name="Novice",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_novice"]),
            hoist=True,
        )

        roles["role_initiate"] = await interaction.guild.create_role(
            name="Initiate",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_initiate"]),
            hoist=True,
        )

        roles["role_rookie"] = await interaction.guild.create_role(
            name="Rookie",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_rookie"]),
            hoist=True,
        )

        roles["role_incompetent"] = await interaction.guild.create_role(
            name="Incompetent",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_incompetent"]),
            hoist=True,
        )

        # Bot Roles
        roles["role_bot"] = await interaction.guild.create_role(
            name="Bot",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_bot"]),
            hoist=True,
        )
        await interaction.guild.me.add_roles(roles["role_bot"])

        # Membership Roles
        if interaction.guild.premium_subscriber_role:
            roles["role_server_booster"] = interaction.guild.premium_subscriber_role
            await interaction.guild.premium_subscriber_role.edit()

        roles["role_judge"] = await interaction.guild.create_role(
            name="Judge",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_judge"]),
            color=ROLE_COLORS["role_judge"],
            hoist=False,
        )

        roles["role_citizen"] = await interaction.guild.create_role(
            name="Citizen",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_citizen"]),
            color=ROLE_COLORS["role_citizen"],
            hoist=False,
        )

        roles["role_member"] = await interaction.guild.create_role(
            name="Member",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_member"]),
            hoist=False,
        )

        roles["role_promoter"] = await interaction.guild.create_role(
            name="Promoter",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_promoter"]),
            hoist=False,
        )

        # Optional Roles
        roles["role_logs"] = await interaction.guild.create_role(
            name="Logs",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_logs"]),
            hoist=False,
        )

        roles["role_events"] = await interaction.guild.create_role(
            name="Events",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_events"]),
            hoist=False,
        )

        roles["role_debate_ping"] = await interaction.guild.create_role(
            name="Debate Ping",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_debate_ping"]),
            hoist=False,
            mentionable=True,
        )

        # Punishment Roles
        roles["role_detained"] = await interaction.guild.create_role(
            name="Detained",
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_detained"]),
            hoist=False,
        )

        # Update Database
        persisted_roles = dict(roles)
        if "role_everyone" in persisted_roles:
            persisted_roles.pop("role_everyone")
        db_guilds = await self.bot.engine.find(GuildModel)
        if len(db_guilds) > 0:
            for db_guild in db_guilds[1:]:
                await self.bot.engine.delete(db_guild)
            guild_instance = db_guilds[0]
            guild_instance.roles = persisted_roles
            await self.bot.engine.save(guild_instance)
        else:
            guild_instance = GuildModel(guild=interaction.guild, roles=persisted_roles)
            await self.bot.engine.save(guild_instance)

        # Update State
        self.bot.state["roles_are_setup"] = True

        # Send Confirmation Message
        await update(
            interaction,
            embed=Embed(
                title="Roles Updated",
                description="Roles have been successfully set up.",
                color=0x2ECC71,
            ),
        )

    @app_commands.command(
        name="channels",
        description="Setup channels required by the bot. This is a dangerous procedure that alters the database.",
    )
    async def channels(self, interaction: discord.Interaction) -> None:
        await update(
            interaction,
            embed=Embed(
                title="Processing Channels",
                description="This may take a while.",
                color=0xF1C40F,
            ),
        )

        if interaction.channel != interaction.guild.rules_channel:
            await update(
                interaction,
                embed=Embed(
                    title="Incorrect Channel",
                    description="This command cannot be run in this channel.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )
            return

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

        # Shortcuts
        guild = interaction.guild
        roles = self.bot.state["map_roles"]
        channels = self.bot.state["map_channels"]

        # Delete All Channels
        skipped_channels = [guild.rules_channel, guild.public_updates_channel]
        for channel in guild.channels:
            if channel not in skipped_channels:
                await channel.delete()

        # Setup Information Category
        channels["category_information"] = await guild.create_category_channel(
            name="Information",
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="information"
            ),
        )

        await guild.rules_channel.edit(
            category=channels["category_information"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="information"
            ),
        )
        channels["tc_rules"] = guild.rules_channel

        channels["tc_about"] = await guild.create_text_channel(
            name="about",
            category=channels["category_information"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="information"
            ),
        )

        channels["tc_announcements"] = await guild.create_text_channel(
            name="announcements",
            category=channels["category_information"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="announcements"
            ),
            news=True,
        )

        await guild.public_updates_channel.edit(
            category=channels["category_information"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="community-updates"
            ),
        )
        channels["tc_community_updates"] = guild.rules_channel

        # Set Positions for Information Category
        await guild.rules_channel.edit(position=2)
        await channels["tc_about"].edit(position=3)
        await channels["tc_announcements"].edit(position=4)
        await guild.public_updates_channel.edit(position=5)

        # Setup Moderation Category
        channels["category_moderation"] = await guild.create_category_channel(
            name="Moderation",
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="moderation"
            ),
        )

        channels["tc_mod_commands"] = await guild.create_text_channel(
            name="mod-commands",
            category=channels["category_moderation"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="moderation"
            ),
        )

        channels["tc_isolation"] = await guild.create_text_channel(
            name="isolation",
            category=channels["category_moderation"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="isolation"
            ),
        )

        # Setup Interface Category
        channels["category_interface"] = await guild.create_category_channel(
            name="Interface",
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="interface"
            ),
        )

        channels["tc_election_feed"] = await guild.create_text_channel(
            name="election-feed",
            category=channels["category_interface"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="interface"
            ),
        )

        channels["tc_debate_feed"] = await guild.create_text_channel(
            name="debate-feed",
            category=channels["category_interface"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="interface"
            ),
        )

        channels["tc_motions"] = await guild.create_text_channel(
            name="motions",
            category=channels["category_interface"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="interface"
            ),
        )

        channels["tc_commands"] = await guild.create_text_channel(
            name="commands",
            category=channels["category_interface"],
            slowmode_delay=5,
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="commands"
            ),
        )

        # Setup Events Category
        channels["category_events"] = await guild.create_category_channel(
            name="Events",
            overwrites=generate_overwrites(interaction, roles=roles, channel="events"),
        )

        # Setup Community Category
        channels["category_community"] = await guild.create_category_channel(
            name="Community",
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="community"
            ),
        )

        channels["tc_general"] = await guild.create_text_channel(
            name="general",
            category=channels["category_community"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="general"),
        )

        channels["tc_memes"] = await guild.create_text_channel(
            name="memes",
            category=channels["category_community"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="community"
            ),
        )

        # Setup Parliament
        channels["category_parliament"] = await guild.create_category_channel(
            name="Parliament",
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="parliament"
            ),
        )

        channels["vc_house_of_lords"] = await guild.create_voice_channel(
            name="House of Lords",
            category=channels["category_parliament"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="parliament"
            ),
        )

        channels["vc_house_of_commons"] = await guild.create_voice_channel(
            name="House of Commons",
            category=channels["category_parliament"],
            overwrites=generate_overwrites(
                interaction, roles=roles, channel="house_of_commons"
            ),
        )

        # Setup Debate Category
        channels["category_debate"] = await guild.create_category_channel(
            name="Debate",
            overwrites=generate_overwrites(interaction, roles=roles, channel="debate"),
        )

        # Setup Logs Category
        channels["category_logs"] = await guild.create_category_channel(
            name="Logs",
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_moderator_actions"] = await guild.create_text_channel(
            name="moderator-actions",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_message_deletion"] = await guild.create_text_channel(
            name="message-deletion",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_message_edits"] = await guild.create_text_channel(
            name="message-edits",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_ban_unban"] = await guild.create_text_channel(
            name="ban-unban",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_nicknames"] = await guild.create_text_channel(
            name="nicknames",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_join_leave"] = await guild.create_text_channel(
            name="join-leave",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_automod"] = await guild.create_text_channel(
            name="automod",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_channels"] = await guild.create_text_channel(
            name="channels",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_invites"] = await guild.create_text_channel(
            name="invites",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_roles"] = await guild.create_text_channel(
            name="roles",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        channels["tc_voice"] = await guild.create_text_channel(
            name="voice",
            category=channels["category_logs"],
            overwrites=generate_overwrites(interaction, roles=roles, channel="logs"),
        )

        # Create Debate Channels
        db_vc_channels = {}
        for _channel_number in range(1, 21):
            channels[f"vc_debate_{_channel_number}"] = await guild.create_voice_channel(
                name=f"Debate {_channel_number}",
                category=channels["category_debate"],
                overwrites=generate_overwrites(
                    interaction, roles=roles, channel="debate"
                ),
            )

            if _channel_number != 1:
                await channels[f"vc_debate_{_channel_number}"].edit(
                    overwrites={
                        roles["role_moderation_bot"]: MODERATION_BOT,
                        roles["role_chancellor"]: NEGATIVE,
                        roles["role_liege"]: NEGATIVE,
                        roles["role_prime_minister"]: NEGATIVE,
                        roles["role_minister"]: NEGATIVE,
                        roles["role_host"]: NEGATIVE,
                        roles["role_bot"]: BASE,
                        roles["role_judge"]: NEGATIVE,
                        roles["role_citizen"]: NEGATIVE,
                        roles["role_member"]: NEGATIVE,
                        roles["role_logs"]: BASE,
                        roles["role_detained"]: NEGATIVE,
                        roles["role_everyone"]: NEGATIVE,
                    }
                )

            db_vc_channels[f"vc_debate_{_channel_number}"] = channels[
                f"vc_debate_{_channel_number}"
            ].id

        # Update Database
        _database_entries = {
            db_entry: channels[db_entry].id for db_entry in DB_CHANNEL_NAME_MAP.values()
        }
        _database_entries.update(db_vc_channels)
        db_guilds = await self.bot.engine.find(GuildModel)
        if len(db_guilds) > 0:
            for db_guild in db_guilds[1:]:
                await self.bot.engine.delete(db_guild)
            guild_instance = db_guilds[0]
            guild_instance.channels = _database_entries
            await self.bot.engine.save(guild_instance)
        else:
            guild_instance = GuildModel(
                guild=interaction.guild, channels=_database_entries
            )
            await self.bot.engine.save(guild_instance)

        # Send Confirmation Message
        await update(
            interaction,
            embed=Embed(
                title="Channels Updated",
                description="Channels have been successfully set up.",
                color=0x2ECC71,
            ),
        )

    @app_commands.command(
        name="icons",
        description="Setup role icons required by the bot.",
    )
    async def icons(self, interaction: discord.Interaction) -> None:
        await update(
            interaction,
            embed=Embed(
                title="Processing Icons",
                description="This may take a while.",
                color=0xF1C40F,
            ),
        )

        at_level_2 = check_level_2(self.bot, interaction)
        if not at_level_2:
            await update(
                interaction,
                embed=Embed(
                    title="Unsatisfied Requirements",
                    description="Please ensure the server is boosted to at least tier 2.",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )

        # Prime Local Cache
        roles = {}
        for role in interaction.guild.roles:
            if not role.managed:
                roles[DB_ROLE_NAME_MAP[role.name]] = role

        # Add Role Icons
        await roles["role_grandmaster"].edit(display_icon="👑")
        await roles["role_legend"].edit(display_icon="🏆")
        await roles["role_master"].edit(display_icon="⚖️")
        await roles["role_expert"].edit(display_icon="⚔️")
        await roles["role_distinguished"].edit(display_icon="💥")
        await roles["role_apprentice"].edit(display_icon="💡")
        await roles["role_novice"].edit(display_icon="🔥")
        await roles["role_initiate"].edit(display_icon="🔰")
        await roles["role_rookie"].edit(display_icon="🧷")
        await roles["role_incompetent"].edit(display_icon="💯")

        # Send Confirmation Message
        await update(
            interaction,
            embed=Embed(
                title="Icons Updated",
                description="Icons have been successfully set up.",
                color=0x2ECC71,
            ),
        )


@app_commands.default_permissions(administrator=True)
class Migrate(commands.GroupCog, name="migrate"):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name="roles",
        description="Add and remove roles required by the bot. This is a dangerous procedure that modifies the server.",
    )
    @check_prerequisites_enabled()
    async def roles(self, interaction: discord.Interaction) -> None:
        guild = self.bot.get_guild(self.bot.config["global"]["guild_id"])

        await update(
            interaction,
            embed=Embed(
                title="Migrating Roles",
                description="This may take a while.",
                color=0xF1C40F,
            ),
        )

        # Check if role exist and that their permissions are correct.
        # If incorrect fix it automatically.
        for role in guild.roles:
            if not role.managed:
                if role.name in DB_ROLE_NAME_MAP.keys():
                    if (
                        role.permissions.value
                        == ROLE_PERMISSIONS[DB_ROLE_NAME_MAP[role.name]]
                    ):
                        if ROLE_COLORS[DB_ROLE_NAME_MAP[role.name]]:
                            if (
                                role.color.value
                                == ROLE_COLORS[DB_ROLE_NAME_MAP[role.name]]
                            ):
                                continue
                            else:
                                await role.edit(
                                    color=ROLE_COLORS[DB_ROLE_NAME_MAP[role.name]]
                                )
                        else:
                            continue
                    else:
                        await role.edit(
                            permissions=Permissions(
                                ROLE_PERMISSIONS[DB_ROLE_NAME_MAP[role.name]]
                            )
                        )
                else:
                    await role.delete()

        db_roles = list(DB_ROLE_NAME_MAP.keys())
        db_roles.remove("@everyone")
        for db_role_name in db_roles:
            role = discord.utils.get(guild.roles, name=db_role_name)
            if ROLE_COLORS[DB_ROLE_NAME_MAP[db_role_name]]:
                if not role:
                    await guild.create_role(
                        name=db_role_name,
                        permissions=Permissions(
                            ROLE_PERMISSIONS[DB_ROLE_NAME_MAP[db_role_name]]
                        ),
                        color=ROLE_COLORS[DB_ROLE_NAME_MAP[db_role_name]],
                        hoist=bool(DB_ROLE_NAME_MAP[db_role_name] in RANK_RATING_MAP),
                    )
            else:
                if not role:
                    await guild.create_role(
                        name=db_role_name,
                        permissions=Permissions(
                            ROLE_PERMISSIONS[DB_ROLE_NAME_MAP[db_role_name]]
                        ),
                        hoist=bool(DB_ROLE_NAME_MAP[db_role_name] in RANK_RATING_MAP),
                    )

        current_positions = {}
        for role in guild.roles:
            current_positions[role.name] = role.position

        positions = {guild.me.top_role: 1}
        db_role_names = {
            _: DB_ROLE_NAME_MAP[_] for _ in DB_ROLE_NAME_MAP if _ != "@everyone"
        }
        for index, db_role_name in enumerate(db_role_names):
            role = discord.utils.get(guild.roles, name=db_role_name)
            positions[role] = index + 2

        managed_roles = []
        for role in guild.roles:
            if role.managed and not role.is_default():
                if role != guild.me.top_role:
                    managed_roles.append(role)

        for index, role in enumerate(managed_roles):
            positions[role] = len(positions) + index + 1

        keys = list(positions.keys())
        values = list(positions.values())[::-1]
        positions = dict(zip(keys, values))
        await guild.edit_role_positions(positions)

        # Prime Local Cache
        roles = {}
        for role in guild.roles:
            if not role.managed and not role.is_default():
                roles[DB_ROLE_NAME_MAP[role.name]] = role

        # Assign Roles
        await guild.owner.add_roles(roles["role_the_crown"])

        # Hoist Roles
        await roles["role_champion"].edit(hoist=True)

        persisted_roles = dict(roles)
        if "role_everyone" in persisted_roles:
            persisted_roles.pop("role_everyone")

        db_guilds = await self.bot.engine.find(GuildModel)
        if len(db_guilds) > 0:
            for db_guild in db_guilds[1:]:
                await self.bot.engine.delete(db_guild)
            guild_instance = db_guilds[0]
            guild_instance.roles = persisted_roles
            await self.bot.engine.save(guild_instance)
        else:
            guild_instance = GuildModel(guild=interaction.guild, roles=persisted_roles)
            await self.bot.engine.save(guild_instance)

        # Send Confirmation Message
        await update(
            interaction,
            embed=Embed(
                title="Roles Migrated",
                description="Missing roles and their permissions have been set up.",
                color=0x2ECC71,
            ),
        )

    @app_commands.command(
        name="channels",
        description="Add and remove channels required by the bot. "
        "This is a dangerous procedure that modifies the server.",
    )
    @check_prerequisites_enabled()
    async def channels(self, interaction: discord.Interaction) -> None:
        guild = self.bot.get_guild(self.bot.config["global"]["guild_id"])

        await update(
            interaction,
            embed=Embed(
                title="Migrating Channels",
                description="This may take a while.",
                color=0xF1C40F,
            ),
        )

        # Prime Local Cache
        roles = {}
        for role in guild.roles:
            if not role.managed:
                roles[DB_ROLE_NAME_MAP[role.name]] = role

        # Delete Channels
        db_guilds = await self.bot.engine.find(GuildModel)
        guild_instance = db_guilds[0]
        channels = guild_instance.channels
        if channels:
            for _category, _channels in guild.by_category():
                if _category:
                    category_id = channels[DB_CHANNEL_NAME_MAP[_category.name]]
                    for _channel in _category.channels:
                        channel_id = channels[DB_CHANNEL_NAME_MAP[_channel.name]]
                        if _channel.id != channel_id:
                            if _channel not in [
                                guild.rules_channel,
                                guild.public_updates_channel,
                            ]:
                                await _channel.delete()

                    if _category.id != category_id:
                        await _category.delete()
                else:
                    for _channel in _channels:
                        channel_id = channels[DB_CHANNEL_NAME_MAP[_channel.name]]
                        if _channel.id != channel_id:
                            if _channel not in [
                                guild.rules_channel,
                                guild.public_updates_channel,
                            ]:
                                await _channel.delete()

        for _channel in guild.channels:
            if _channel.name not in DB_CHANNEL_NAME_MAP.keys():
                await _channel.delete()

        # Create and Update Channels
        for channel_name in DB_CHANNEL_NAME_MAP.keys():
            _channel = discord.utils.get(guild.channels, name=channel_name)
            if not _channel:
                if DB_CHANNEL_NAME_MAP[channel_name].startswith("category"):
                    await guild.create_category_channel(
                        name=channel_name,
                        overwrites=generate_overwrites(
                            interaction,
                            roles=roles,
                            channel=DB_CHANNEL_NAME_MAP[channel_name],
                        ),
                    )
                elif DB_CHANNEL_NAME_MAP[channel_name].startswith("tc"):
                    if channel_name == "announcements":
                        await guild.create_text_channel(
                            name=channel_name,
                            overwrites=generate_overwrites(
                                interaction,
                                roles=roles,
                                channel=DB_CHANNEL_NAME_MAP[channel_name],
                            ),
                            news=True,
                        )
                    else:
                        await guild.create_text_channel(
                            name=channel_name,
                            overwrites=generate_overwrites(
                                interaction,
                                roles=roles,
                                channel=DB_CHANNEL_NAME_MAP[channel_name],
                            ),
                        )
                elif DB_CHANNEL_NAME_MAP[channel_name].startswith("vc"):
                    if "debate" in DB_CHANNEL_NAME_MAP[channel_name]:
                        if not DB_CHANNEL_NAME_MAP[channel_name].endswith(" 1"):
                            await guild.create_voice_channel(
                                name=channel_name,
                                overwrites={
                                    roles["role_moderation_bot"]: MODERATION_BOT,
                                    roles["role_chancellor"]: NEGATIVE,
                                    roles["role_liege"]: NEGATIVE,
                                    roles["role_prime_minister"]: NEGATIVE,
                                    roles["role_minister"]: NEGATIVE,
                                    roles["role_host"]: NEGATIVE,
                                    roles["role_bot"]: BASE,
                                    roles["role_judge"]: NEGATIVE,
                                    roles["role_citizen"]: NEGATIVE,
                                    roles["role_member"]: NEGATIVE,
                                    roles["role_promoter"]: NEGATIVE,
                                    roles["role_logs"]: BASE,
                                    roles["role_detained"]: NEGATIVE,
                                    roles["role_everyone"]: NEGATIVE,
                                },
                            )
                        else:
                            await guild.create_voice_channel(
                                name=channel_name,
                                overwrites=generate_overwrites(
                                    interaction, roles=roles, channel="debate"
                                ),
                            )
                    else:
                        await guild.create_voice_channel(
                            name=channel_name,
                            overwrites=generate_overwrites(
                                interaction,
                                roles=roles,
                                channel=DB_CHANNEL_NAME_MAP[channel_name],
                            ),
                        )
            else:
                for channel_name in DB_CHANNEL_NAME_MAP.keys():
                    if channel_name == _channel.name:
                        break

                overwrites = generate_overwrites(
                    interaction, roles=roles, channel=channel_name
                )

                if _channel.name.startswith("Debate"):
                    if not _channel.name.endswith(" 1"):
                        overwrites = {
                            roles["role_moderation_bot"]: MODERATION_BOT,
                            roles["role_chancellor"]: NEGATIVE,
                            roles["role_liege"]: NEGATIVE,
                            roles["role_prime_minister"]: NEGATIVE,
                            roles["role_minister"]: NEGATIVE,
                            roles["role_host"]: NEGATIVE,
                            roles["role_bot"]: BASE,
                            roles["role_judge"]: NEGATIVE,
                            roles["role_citizen"]: NEGATIVE,
                            roles["role_member"]: NEGATIVE,
                            roles["role_logs"]: BASE,
                            roles["role_detained"]: NEGATIVE,
                            roles["role_everyone"]: NEGATIVE,
                        }
                        if _channel.overwrites != overwrites:
                            await _channel.edit(overwrites=overwrites)
                    else:
                        if _channel.overwrites != overwrites:
                            await _channel.edit(overwrites=overwrites)
                else:
                    if _channel.overwrites != overwrites:
                        await _channel.edit(overwrites=overwrites)

        # Reorder Channels
        for category_name in CHANNEL_SORT_ORDER.keys():
            category = discord.utils.get(guild.channels, name=category_name)
            position = list(CHANNEL_SORT_ORDER.keys()).index(category_name)
            await category.edit(position=position)

        for category_name in CHANNEL_SORT_ORDER.keys():
            category = discord.utils.get(guild.channels, name=category_name)
            sorted_channels = []
            for channel_name in CHANNEL_SORT_ORDER[category_name]:
                channel = discord.utils.get(guild.channels, name=channel_name)
                sorted_channels.append(channel)

            if sorted_channels:
                min_position = min(sorted_channels, key=lambda c: c.position)
                for new_position, channel in enumerate(
                    sorted_channels, start=min_position.position
                ):
                    await channel.edit(category=category, position=new_position)

        # Update Database
        _database_entries = {
            DB_CHANNEL_NAME_MAP[db_entry.name]: db_entry for db_entry in guild.channels
        }
        db_guilds = await self.bot.engine.find(GuildModel)
        if len(db_guilds) > 0:
            for db_guild in db_guilds[1:]:
                await self.bot.engine.delete(db_guild)
            guild_instance = db_guilds[0]
            guild_instance.channels = _database_entries
            await self.bot.engine.save(guild_instance)
        else:
            guild_instance = GuildModel(
                guild=interaction.guild, channels=_database_entries
            )
            await self.bot.engine.save(guild_instance)

        # Send Confirmation Message
        await update(
            interaction,
            embed=Embed(
                title="Channels Migrated",
                description="Missing channels and their permissions have been set up.",
                color=0x2ECC71,
            ),
        )


async def setup(bot: ArgusClient) -> None:
    await bot.add_cog(
        Setup(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
    await bot.add_cog(
        Migrate(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
