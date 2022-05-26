DB_ROLE_NAME_MAP = {
    "Warden": "role_warden",
    "The Crown": "role_the_crown",
    "Moderation Bot": "role_moderation_bot",
    "Chancellor": "role_chancellor",
    "Liege": "role_liege",
    "Prime Minister": "role_prime_minister",
    "Minister": "role_minister",
    "Host": "role_host",
    "Grandmaster": "role_grandmaster",
    "Legend": "role_legend",
    "Master": "role_master",
    "Expert": "role_expert",
    "Distinguished": "role_distinguished",
    "Apprentice": "role_apprentice",
    "Novice": "role_novice",
    "Initiate": "role_initiate",
    "Rookie": "role_rookie",
    "Incompetent": "role_incompetent",
    "Bot": "role_bot",
    "Citizen": "role_citizen",
    "Logs": "role_logs",
    "Events": "role_events",
    "Debate Ping": "role_debate_ping",
    "Detained": "role_detained",
    "@everyone": "role_everyone",
}

DB_CHANNEL_NAME_MAP = {
    "Information": "category_information",
    "rules": "tc_rules",
    "about": "tc_about",
    "announcements": "tc_announcements",
    "community-updates": "tc_community_updates",
    "Moderation": "category_moderation",
    "mod-commands": "tc_mod_commands",
    "isolation": "tc_isolation",
    "Interface": "category_interface",
    "debate-feed": "tc_debate_feed",
    "commands": "tc_commands",
    "Events": "category_events",
    "Community": "category_community",
    "general": "tc_general",
    "memes": "tc_memes",
    "Debate": "category_debate",
    "Lounge": "category_lounge",
    "Logs": "category_logs",
    "moderator-actions": "tc_moderator_actions",
    "message-deletion": "tc_message_deletion",
    "message-edits": "tc_message_edits",
    "ban-unban": "tc_ban_unban",
    "nicknames": "tc_nicknames",
    "join-leave": "tc_join_leave",
    "automod": "tc_automod",
    "channels": "tc_channels",
    "invites": "tc_invites",
    "roles": "tc_roles",
    "voice": "tc_voice",
}

for _channel_number in range(1, 21):
    DB_CHANNEL_NAME_MAP[f"debate-{_channel_number}"] = f"tc_debate_{_channel_number}"
    DB_CHANNEL_NAME_MAP[f"Debate {_channel_number}"] = f"vc_debate_{_channel_number}"


RANK_RATING_MAP = {
    "role_grandmaster": 1333 + 1 / 3,
    "role_legend": 1250,
    "role_master": 1166 + 2 / 3,
    "role_expert": 1083 + 1 / 3,
    "role_distinguished": 1000,
    "role_apprentice": 583 + 1 / 3,
    "role_novice": 500,
    "role_initiate": 416 + 2 / 3,
    "role_rookie": 83 + 1 / 3,
    "role_incompetent": 0,
}

ROLE_PERMISSIONS = {
    "role_warden": 0,
    "role_the_crown": 0,
    "role_moderation_bot": 1089042513857,
    "role_chancellor": 1098639081441,
    "role_liege": 1098639081409,
    "role_prime_minister": 1097564815169,
    "role_minister": 1097564815169,
    "role_host": 0,
    "role_grandmaster": 0,
    "role_legend": 0,
    "role_master": 0,
    "role_expert": 0,
    "role_distinguished": 0,
    "role_apprentice": 0,
    "role_novice": 0,
    "role_initiate": 0,
    "role_rookie": 0,
    "role_incompetent": 0,
    "role_bot": 0,
    "role_citizen": 2251673153,
    "role_logs": 0,
    "role_events": 0,
    "role_debate_ping": 0,
    "role_detained": 0,
    "role_everyone": 2184252480,
}

# Bot Global Strings
BOT_DESCRIPTION = "Elections and Debates for Discord Servers"

# Bot Plugins Directories
PLUGINS = ["plugins.layout", "plugins.meta"]
