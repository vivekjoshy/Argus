import asyncio
from queue import Queue

from argus.client import ArgusClient


async def debate_feed_updater(bot: ArgusClient):
    while bot.state["debates_enabled"]:
        fifo: Queue = bot.state["debate_feed_fifo"]
        while fifo.qsize() > 0:
            embed = fifo.get()
            debate_feed = bot.state["map_channels"]["tc_debate_feed"]
            await debate_feed.send(embed=embed)
        await asyncio.sleep(0.5)
