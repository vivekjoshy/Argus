import discord
from discord import app_commands, Embed, Permissions
from discord.ext import commands

from argus.checks import check_prerequisites_enabled
from argus.client import ArgusClient
from argus.constants import ROLE_PERMISSIONS
from argus.utils import update


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

        roles["role_citizen"] = discord.utils.get(
            interaction.guild.roles, name="Citizen"
        )
        roles["role_member"] = discord.utils.get(interaction.guild.roles, name="Member")
        roles["role_everyone"] = interaction.guild.default_role

        await roles["role_citizen"].edit(
            permissions=Permissions(permissions=137474982912)
        )
        await roles["role_member"].edit(
            permissions=Permissions(permissions=137474982912)
        )
        await roles["role_everyone"].edit(permissions=Permissions(permissions=35718144))

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

        # Shortcut Variables
        channels = self.bot.state["map_channels"]
        roles = self.bot.state["map_roles"]

        roles["role_citizen"] = discord.utils.get(
            interaction.guild.roles, name="Citizen"
        )
        roles["role_member"] = discord.utils.get(interaction.guild.roles, name="Member")
        roles["role_everyone"] = interaction.guild.default_role

        await roles["role_citizen"].edit(
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_citizen"])
        )
        await roles["role_member"].edit(
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_member"])
        )
        await roles["role_everyone"].edit(
            permissions=Permissions(permissions=ROLE_PERMISSIONS["role_everyone"])
        )

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
