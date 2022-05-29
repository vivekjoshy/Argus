import discord
from discord.ext import commands

from argus.client import ArgusClient


class Global(commands.Cog):
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


async def setup(bot: ArgusClient) -> None:
    await bot.add_cog(
        Global(bot), guilds=[discord.Object(id=bot.config["global"]["guild_id"])]
    )
