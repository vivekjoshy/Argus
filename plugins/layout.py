import asyncio

import discord
from discord import app_commands, Embed, Permissions
from discord.ext import commands

from argus.client import ArgusClient


@app_commands.default_permissions(administrator=True)
class Layout(commands.GroupCog, name="setup"):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot
        super().__init__()

        # Setup Roles
        self.bot.state["map_roles"] = {
            "role_warden": None,
            "role_first_citizen": None,
            "role_staff_director": None,
            "role_staff_moderator": None,
            "role_community_director": None,
            "role_community_moderator" "role_host": None,
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
            "role_citizen": None,
            "role_events": None,
            "role_logs": None,
            "role_debate_ping": None,
            "role_detained": None,
            "role_everyone": None,
        }

    @app_commands.command(
        name="roles",
        description="Setup roles required by the bot. This is a dangerous procedure that alters the database.",
    )
    async def roles(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embed=Embed(
                title="Processing Roles",
                description="This may take a while.",
                color=0xF1C40F,
            )
        )

        if self.bot.state["roles_are_setup"]:
            await interaction.edit_original_message(
                embed=Embed(
                    title="Roles Already Set Up",
                    description="Please restart the bot manually if your still want to overwrite roles.",
                    color=0xE74C3C,
                )
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
            permissions=Permissions(permissions=2184252480)
        )

        # Setup Power Roles
        roles["role_warden"] = await interaction.guild.create_role(
            name="Warden",
            permissions=Permissions(permissions=8),
            colour=0xEB6A5C,
            hoist=False,
        )
        await interaction.guild.me.add_roles(roles["role_warden"])

        roles["role_the_crown"] = await interaction.guild.create_role(
            name="The Crown",
            colour=0xD4AF37,
            permissions=Permissions(permissions=0),
            hoist=False,
        )
        await interaction.guild.owner.add_roles(roles["role_the_crown"])

        roles["role_chancellor"] = await interaction.guild.create_role(
            name="Chancellor",
            colour=0x9B59B6,
            permissions=Permissions(permissions=1098639081441),
            hoist=False,
        )

        roles["role_liege"] = await interaction.guild.create_role(
            name="Liege",
            colour=0xE67E22,
            permissions=Permissions(permissions=1098639081409),
            hoist=False,
        )

        roles["role_prime_minister"] = await interaction.guild.create_role(
            name="Prime Minister",
            colour=0xE74C3C,
            permissions=Permissions(permissions=1097564815169),
            hoist=False,
        )

        roles["role_minister"] = await interaction.guild.create_role(
            name="Minister",
            colour=0x2ECC71,
            permissions=Permissions(permissions=1097564815169),
            hoist=False,
        )

        # Selective Permissions
        roles["role_host"] = await interaction.guild.create_role(
            name="Host", permissions=Permissions(permissions=0), hoist=False
        )

        # Setup Rated Roles
        roles["role_grandmaster"] = await interaction.guild.create_role(
            name="Grandmaster", permissions=Permissions(permissions=0), hoist=True
        )

        roles["role_legend"] = await interaction.guild.create_role(
            name="Legend", permissions=Permissions(permissions=0), hoist=True
        )

        roles["role_master"] = await interaction.guild.create_role(
            name="Master", permissions=Permissions(permissions=0), hoist=True
        )

        roles["role_expert"] = await interaction.guild.create_role(
            name="Expert", permissions=Permissions(permissions=0), hoist=True
        )

        roles["role_distinguished"] = await interaction.guild.create_role(
            name="Distinguished", permissions=Permissions(permissions=0), hoist=True
        )

        roles["role_apprentice"] = await interaction.guild.create_role(
            name="Apprentice", permissions=Permissions(permissions=0), hoist=True
        )

        roles["role_novice"] = await interaction.guild.create_role(
            name="Novice", permissions=Permissions(permissions=0), hoist=True
        )

        roles["role_initiate"] = await interaction.guild.create_role(
            name="Initiate", permissions=Permissions(permissions=0), hoist=True
        )

        roles["role_rookie"] = await interaction.guild.create_role(
            name="Rookie", permissions=Permissions(permissions=0), hoist=True
        )

        roles["role_incompetent"] = await interaction.guild.create_role(
            name="Incompetent", permissions=Permissions(permissions=0), hoist=True
        )

        # Bot Roles
        roles["role_bot"] = await interaction.guild.create_role(
            name="Bot", permissions=Permissions(permissions=0), hoist=True
        )
        await interaction.guild.me.add_roles(roles["role_bot"])

        # Membership Roles
        roles["role_citizen"] = await interaction.guild.create_role(
            name="Citizen", permissions=Permissions(permissions=2251673153), hoist=False
        )

        # Optional Roles
        roles["role_logs"] = await interaction.guild.create_role(
            name="Logs", permissions=Permissions(permissions=0), hoist=False
        )

        roles["role_events"] = await interaction.guild.create_role(
            name="Events", permissions=Permissions(permissions=0), hoist=False
        )

        # todo: ping automatically when someone risks their skill rating
        roles["role_debate_ping"] = await interaction.guild.create_role(
            name="Debate Ping", permissions=Permissions(permissions=0), hoist=False
        )

        # Punishment Roles
        roles["role_detained"] = await interaction.guild.create_role(
            name="Detained", permissions=Permissions(permissions=0), hoist=False
        )

        # Update Database
        await self.bot.db.upsert(
            interaction.guild,
            role_warden=roles["role_warden"].id,
            role_the_crown=roles["role_the_crown"].id,
            role_chancellor=roles["role_chancellor"].id,
            role_liege=roles["role_liege"].id,
            role_prime_minister=roles["role_prime_minister"].id,
            role_host=roles["role_host"].id,
            role_grandmaster=roles["role_grandmaster"].id,
            role_legend=roles["role_legend"].id,
            role_master=roles["role_master"].id,
            role_expert=roles["role_expert"].id,
            role_distinguished=roles["role_distinguished"].id,
            role_apprentice=roles["role_apprentice"].id,
            role_novice=roles["role_novice"].id,
            role_initiate=roles["role_initiate"].id,
            role_rookie=roles["role_rookie"].id,
            role_incompetent=roles["role_incompetent"].id,
            role_bot=roles["role_bot"].id,
            role_citizen=roles["role_citizen"].id,
            role_events=roles["role_events"].id,
            role_logs=roles["role_logs"].id,
            role_debate_ping=roles["role_debate_ping"].id,
            role_detained=roles["role_detained"].id,
        )

        # Update State
        self.bot.state["roles_are_setup"] = True

        # Send Confirmation Message
        await interaction.edit_original_message(
            embed=Embed(
                title="Roles Updated",
                description="Roles have been successfully set up.",
                color=0x2ECC71,
            )
        )


async def setup(bot: ArgusClient) -> None:
    await bot.add_cog(
        Layout(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
