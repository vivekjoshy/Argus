from discord import PermissionOverwrite, Interaction

from argus.constants import CHANNEL_SORT_ORDER

BASE = PermissionOverwrite()
INVITE = PermissionOverwrite(
    create_instant_invite=True,
)
NEGATIVE = PermissionOverwrite(view_channel=False)
POSITIVE = PermissionOverwrite(view_channel=True)
EXPLICIT_READ_MESSAGE_HISTORY_ONLY = PermissionOverwrite(
    read_messages=True,
    read_message_history=True,
    add_reactions=False,
    send_messages=False,
    manage_messages=False,
    embed_links=False,
    attach_files=False,
    manage_threads=False,
    create_public_threads=False,
    create_private_threads=False,
    send_messages_in_threads=False,
)
READ_MESSAGE_HISTORY_ONLY = PermissionOverwrite(
    view_channel=True,
    add_reactions=False,
    send_messages=False,
    manage_messages=False,
    embed_links=False,
    attach_files=False,
    manage_threads=False,
    create_public_threads=False,
    create_private_threads=False,
    send_messages_in_threads=False,
)
INVITE_READ_MESSAGE_HISTORY_ONLY = PermissionOverwrite(
    create_instant_invite=True,
    add_reactions=False,
    send_messages=False,
    manage_messages=False,
    embed_links=False,
    attach_files=False,
    manage_threads=False,
    create_public_threads=False,
    create_private_threads=False,
    send_messages_in_threads=False,
)
GENERAL = PermissionOverwrite(
    create_instant_invite=True,
    embed_links=False,
    attach_files=False,
)
ANNOUNCEMENT_ELEVATED = PermissionOverwrite(
    send_messages=True,
    manage_messages=True,
    embed_links=True,
    attach_files=True,
    manage_threads=False,
    create_public_threads=False,
    create_private_threads=False,
    send_messages_in_threads=False,
)
ANNOUNCEMENT = PermissionOverwrite(
    send_messages=True,
    add_reactions=False,
    manage_messages=False,
    manage_threads=False,
    create_public_threads=False,
    create_private_threads=False,
    send_messages_in_threads=False,
)
ANNOUNCEMENT_MANAGE_ONLY = PermissionOverwrite(
    manage_messages=False,
    add_reactions=False,
    send_messages=False,
    embed_links=False,
    attach_files=False,
    create_public_threads=False,
    create_private_threads=False,
    send_messages_in_threads=False,
)
MODERATION_TEAM = PermissionOverwrite(
    view_channel=True,
    add_reactions=False,
    manage_messages=False,
    manage_threads=False,
    create_public_threads=False,
    create_private_threads=False,
    send_messages_in_threads=False,
)
DEBATE_TEXT_DENY = PermissionOverwrite(
    add_reactions=False,
    send_messages=False,
    embed_links=False,
    attach_files=False,
)
EVENTS_MANAGE = PermissionOverwrite(
    request_to_speak=True,
    manage_events=True,
    view_channel=True,
    manage_channels=True,
    manage_messages=True,
    add_reactions=True,
    send_messages=True,
    embed_links=True,
    attach_files=True,
    create_public_threads=True,
    send_messages_in_threads=True,
    create_private_threads=False,
)
EVENTS = PermissionOverwrite(
    request_to_speak=True,
    create_instant_invite=True,
)
MODERATION_BOT = PermissionOverwrite(
    read_messages=True,
    read_message_history=True,
    add_reactions=True,
    send_messages=True,
    manage_messages=True,
    embed_links=True,
    attach_files=True,
    manage_threads=True,
    create_public_threads=True,
    create_private_threads=True,
    send_messages_in_threads=True,
)

OVERWRITE_MAP = {
    "information": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": READ_MESSAGE_HISTORY_ONLY,
        "role_liege": READ_MESSAGE_HISTORY_ONLY,
        "role_prime_minister": READ_MESSAGE_HISTORY_ONLY,
        "role_minister": READ_MESSAGE_HISTORY_ONLY,
        "role_host": READ_MESSAGE_HISTORY_ONLY,
        "role_bot": BASE,
        "role_citizen": INVITE_READ_MESSAGE_HISTORY_ONLY,
        "role_member": INVITE_READ_MESSAGE_HISTORY_ONLY,
        "role_logs": BASE,
        "role_detained": NEGATIVE,
        "role_everyone": INVITE_READ_MESSAGE_HISTORY_ONLY,
    },
    "announcements": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": ANNOUNCEMENT_ELEVATED,
        "role_liege": ANNOUNCEMENT_MANAGE_ONLY,
        "role_prime_minister": ANNOUNCEMENT_ELEVATED,
        "role_minister": READ_MESSAGE_HISTORY_ONLY,
        "role_host": ANNOUNCEMENT,
        "role_bot": BASE,
        "role_citizen": INVITE_READ_MESSAGE_HISTORY_ONLY,
        "role_member": INVITE_READ_MESSAGE_HISTORY_ONLY,
        "role_logs": BASE,
        "role_detained": NEGATIVE,
        "role_everyone": INVITE_READ_MESSAGE_HISTORY_ONLY,
    },
    "community-updates": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": READ_MESSAGE_HISTORY_ONLY,
        "role_liege": NEGATIVE,
        "role_prime_minister": NEGATIVE,
        "role_minister": NEGATIVE,
        "role_host": BASE,
        "role_bot": BASE,
        "role_citizen": NEGATIVE,
        "role_member": NEGATIVE,
        "role_logs": BASE,
        "role_detained": NEGATIVE,
        "role_everyone": NEGATIVE,
    },
    "moderation": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": MODERATION_TEAM,
        "role_liege": MODERATION_TEAM,
        "role_prime_minister": MODERATION_TEAM,
        "role_minister": MODERATION_TEAM,
        "role_host": BASE,
        "role_bot": BASE,
        "role_citizen": NEGATIVE,
        "role_member": NEGATIVE,
        "role_logs": BASE,
        "role_detained": NEGATIVE,
        "role_everyone": NEGATIVE,
    },
    "isolation": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": NEGATIVE,
        "role_liege": NEGATIVE,
        "role_prime_minister": NEGATIVE,
        "role_minister": NEGATIVE,
        "role_host": BASE,
        "role_bot": BASE,
        "role_citizen": NEGATIVE,
        "role_member": NEGATIVE,
        "role_logs": BASE,
        "role_detained": EXPLICIT_READ_MESSAGE_HISTORY_ONLY,
        "role_everyone": NEGATIVE,
    },
    "interface": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": INVITE_READ_MESSAGE_HISTORY_ONLY,
        "role_liege": INVITE_READ_MESSAGE_HISTORY_ONLY,
        "role_prime_minister": INVITE_READ_MESSAGE_HISTORY_ONLY,
        "role_minister": INVITE_READ_MESSAGE_HISTORY_ONLY,
        "role_host": BASE,
        "role_bot": BASE,
        "role_citizen": INVITE_READ_MESSAGE_HISTORY_ONLY,
        "role_member": INVITE_READ_MESSAGE_HISTORY_ONLY,
        "role_logs": BASE,
        "role_detained": NEGATIVE,
        "role_everyone": INVITE_READ_MESSAGE_HISTORY_ONLY,
    },
    "commands": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": INVITE,
        "role_liege": INVITE,
        "role_prime_minister": INVITE,
        "role_minister": INVITE,
        "role_host": BASE,
        "role_bot": BASE,
        "role_citizen": INVITE,
        "role_member": INVITE,
        "role_logs": BASE,
        "role_detained": NEGATIVE,
        "role_everyone": INVITE,
    },
    "events": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": EVENTS_MANAGE,
        "role_liege": EVENTS_MANAGE,
        "role_prime_minister": EVENTS_MANAGE,
        "role_minister": BASE,
        "role_host": EVENTS_MANAGE,
        "role_bot": BASE,
        "role_citizen": EVENTS,
        "role_member": EVENTS,
        "role_logs": BASE,
        "role_detained": NEGATIVE,
        "role_everyone": INVITE,
    },
    "community": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": INVITE,
        "role_liege": INVITE,
        "role_prime_minister": INVITE,
        "role_minister": INVITE,
        "role_host": BASE,
        "role_bot": BASE,
        "role_citizen": INVITE,
        "role_member": INVITE,
        "role_logs": BASE,
        "role_detained": NEGATIVE,
        "role_everyone": INVITE,
    },
    "general": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": GENERAL,
        "role_liege": GENERAL,
        "role_prime_minister": GENERAL,
        "role_minister": GENERAL,
        "role_host": BASE,
        "role_bot": BASE,
        "role_citizen": GENERAL,
        "role_member": GENERAL,
        "role_logs": BASE,
        "role_detained": NEGATIVE,
        "role_everyone": GENERAL,
    },
    "debate": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": DEBATE_TEXT_DENY,
        "role_liege": DEBATE_TEXT_DENY,
        "role_prime_minister": DEBATE_TEXT_DENY,
        "role_minister": DEBATE_TEXT_DENY,
        "role_host": BASE,
        "role_bot": BASE,
        "role_citizen": DEBATE_TEXT_DENY,
        "role_member": DEBATE_TEXT_DENY,
        "role_logs": BASE,
        "role_detained": NEGATIVE,
        "role_everyone": DEBATE_TEXT_DENY,
    },
    "logs": {
        "role_moderation_bot": MODERATION_BOT,
        "role_chancellor": READ_MESSAGE_HISTORY_ONLY,
        "role_liege": READ_MESSAGE_HISTORY_ONLY,
        "role_prime_minister": NEGATIVE,
        "role_minister": NEGATIVE,
        "role_host": BASE,
        "role_bot": BASE,
        "role_citizen": NEGATIVE,
        "role_member": NEGATIVE,
        "role_logs": READ_MESSAGE_HISTORY_ONLY,
        "role_detained": NEGATIVE,
        "role_everyone": NEGATIVE,
    },
}


def generate_overwrites(interaction: Interaction, roles, channel: str):
    """
    A dict of roles and their overwrites for a specific channel.
    """
    if channel.lower() not in OVERWRITE_MAP:
        if channel not in CHANNEL_SORT_ORDER.keys():
            for category in CHANNEL_SORT_ORDER.keys():
                channel = channel.replace("_", "-")
                if channel in CHANNEL_SORT_ORDER[category]:
                    channel = category
                    break

    overwrites = OVERWRITE_MAP[channel.lower()]
    return {
        roles["role_moderation_bot"]: overwrites["role_moderation_bot"],
        roles["role_chancellor"]: overwrites["role_chancellor"],
        roles["role_liege"]: overwrites["role_liege"],
        roles["role_prime_minister"]: overwrites["role_prime_minister"],
        roles["role_minister"]: overwrites["role_minister"],
        roles["role_host"]: overwrites["role_host"],
        roles["role_bot"]: overwrites["role_bot"],
        roles["role_citizen"]: overwrites["role_citizen"],
        roles["role_member"]: overwrites["role_member"],
        roles["role_logs"]: overwrites["role_logs"],
        roles["role_detained"]: overwrites["role_detained"],
        interaction.guild.default_role: overwrites["role_everyone"],
    }
