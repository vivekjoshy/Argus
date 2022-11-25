import asyncio
from queue import PriorityQueue

from discord import VoiceChannel

from argus.client import ArgusClient
from argus.overwrites import BASE, MODERATION_BOT, NEGATIVE


def vc_is_visible(bot: ArgusClient, vc: VoiceChannel):
    parent = vc.category
    return parent.overwrites == vc.overwrites


def vc_is_empty(bot: ArgusClient, vc: VoiceChannel):
    return len(vc.members) == 0


async def make_vc_visible(bot: ArgusClient, vc: VoiceChannel):
    await vc.edit(sync_permissions=True)


async def make_vc_invisible(bot: ArgusClient, vc: VoiceChannel):
    roles = bot.state["map_roles"]
    await vc.edit(
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
        }
    )


async def voice_channel_update(bot: ArgusClient):
    while bot.state["debates_enabled"]:
        empty_rooms = PriorityQueue(maxsize=0)
        non_empty_rooms = PriorityQueue(maxsize=0)
        invisible_rooms = PriorityQueue(maxsize=0)
        visible_rooms = PriorityQueue(maxsize=0)
        empty_invisible_rooms = PriorityQueue(maxsize=0)
        empty_visible_rooms = PriorityQueue(maxsize=0)
        non_empty_invisible_rooms = PriorityQueue(maxsize=0)
        non_empty_visible_rooms = PriorityQueue(maxsize=0)

        debate_rooms = bot.state["debate_rooms"]
        for room in debate_rooms:
            vc = room.vc
            if vc_is_empty(bot, vc):
                empty_rooms.put(room)
                if not vc_is_visible(bot, vc):
                    empty_invisible_rooms.put(room)
                else:
                    empty_visible_rooms.put(room)
            else:
                non_empty_rooms.put(room)
                if not vc_is_visible(bot, vc):
                    non_empty_invisible_rooms.put(room)
                else:
                    non_empty_visible_rooms.put(room)

            if not vc_is_visible(bot, vc):
                invisible_rooms.put(room)
            else:
                visible_rooms.put(room)

        if empty_visible_rooms.empty():
            empty_invisible_room = empty_invisible_rooms.get()
            vc = empty_invisible_room.vc
            await make_vc_visible(bot, vc)
            visible_rooms.put(empty_invisible_room)
        else:
            if empty_visible_rooms.qsize() > 1:
                for room in empty_visible_rooms.queue[1:]:
                    vc = room.vc
                    await make_vc_invisible(bot, vc)

        await asyncio.sleep(1)
