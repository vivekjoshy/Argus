import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Context

from argus.client import ArgusClient


class Meta(commands.Cog):
    def __init__(self, bot: ArgusClient) -> None:
        self.bot = bot
        super().__init__()

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx: Context) -> None:
        await ctx.send(
            embed=Embed(
                title="Commands Syncing",
                description="Manual syncing of commands invoked.",
                color=0xF1C40F,
            )
        )

        await ctx.bot.tree.sync(
            guild=discord.Object(id=self.bot.config["global"]["guild_id"])
        )

        await ctx.send(
            embed=Embed(
                title="Commands Synced",
                description="Commands have finished syncing.",
                color=0x2ECC71,
            )
        )


async def setup(bot: ArgusClient) -> None:
    await bot.add_cog(
        Meta(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
