DB_ROLE_NAME_MAP = {
    "Warden": "role_warden",
    "The Crown": "role_the_crown",
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
    "Events": "role_events",
    "Logs": "role_logs",
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
    "director-commands": "tc_director_commands",
    "mod-commands": "tc_mod_commands",
    "isolation": "tc_isolation",
    "Interface": "category_interface",
    "debate-feed": "tc_debate_feed",
    "commands": "tc_commands",
    "Events": "category_events",
    "Community": "category_community",
    "general": "tc_general",
    "serious": "tc_serious",
    "meme-dump": "tc_meme_dump",
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

# Bot Global Strings
BOT_DESCRIPTION = "Elections and Debates for Discord Servers"

# Bot Plugins Directories
PLUGINS = ["plugins.layout", "plugins.meta"]
