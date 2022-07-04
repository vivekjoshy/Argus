DB_ROLE_NAME_MAP = {
    "Warden": "role_warden",
    "The Crown": "role_the_crown",
    "Moderation Bot": "role_moderation_bot",
    "Chancellor": "role_chancellor",
    "Liege": "role_liege",
    "Prime Minister": "role_prime_minister",
    "Minister": "role_minister",
    "Host": "role_host",
    "Champion": "role_champion",
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
    "Judge": "role_judge",
    "Citizen": "role_citizen",
    "Member": "role_member",
    "Promoter": "role_promoter",
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
    "election-feed": "tc_election_feed",
    "debate-feed": "tc_debate_feed",
    "motions": "tc_motions",
    "commands": "tc_commands",
    "Events": "category_events",
    "Community": "category_community",
    "general": "tc_general",
    "memes": "tc_memes",
    "Parliament": "category_parliament",
    "House of Lords": "vc_house_of_lords",
    "House of Commons": "vc_house_of_commons",
    "Debate": "category_debate",
}

for _channel_number in range(1, 21):
    DB_CHANNEL_NAME_MAP[f"Debate {_channel_number}"] = f"vc_debate_{_channel_number}"

DB_CHANNEL_NAME_MAP.update(
    {
        "Partners": "category_partners",
        "similar": "tc_similar",
        "awesome": "tc_awesome",
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
)

CHANNEL_SORT_ORDER = {}
cached_channel_name = None
for channel_name, db_channel_name in DB_CHANNEL_NAME_MAP.items():
    if db_channel_name.startswith("category"):
        CHANNEL_SORT_ORDER[channel_name] = []
        cached_channel_name = channel_name
    elif db_channel_name.startswith("tc") or db_channel_name.startswith("vc"):
        CHANNEL_SORT_ORDER[cached_channel_name].append(channel_name)


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
    "role_moderation_bot": 1632355483073,
    "role_chancellor": 1643025792448,
    "role_liege": 1643025792320,
    "role_prime_minister": 1634435857728,
    "role_minister": 517715000640,
    "role_host": 0,
    "role_champion": 0,
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
    "role_judge": 517580639296,
    "role_server_booster": 1067336453696,
    "role_citizen": 517580639296,
    "role_member": 517580639296,
    "role_promoter": 1067336453696,
    "role_logs": 0,
    "role_events": 0,
    "role_debate_ping": 0,
    "role_detained": 0,
    "role_everyone": 2184252480,
}

ROLE_COLORS = {
    "role_warden": 0xEB6A5C,
    "role_the_crown": 0xD4AF37,
    "role_moderation_bot": None,
    "role_chancellor": 0x9B59B6,
    "role_liege": 0xE74C3C,
    "role_prime_minister": 0xE91E63,
    "role_minister": 0x2ECC71,
    "role_host": None,
    "role_champion": None,
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
    "role_judge": 0xE67E22,
    "role_server_booster": None,
    "role_citizen": 0x3498DB,
    "role_member": None,
    "role_promoter": None,
    "role_logs": None,
    "role_events": None,
    "role_debate_ping": None,
    "role_detained": None,
    "role_everyone": None,
}

# Bot Global Strings
BOT_DESCRIPTION = "Elections and Debates for Discord Servers"

# Bot Plugins Directories
PLUGINS = [
    "plugins.debate",
    "plugins.election",
    "plugins.global",
    "plugins.layout",
    "plugins.meta",
    "plugins.parliament",
    "plugins.security",
]


if __name__ == "__main__":
    print(CHANNEL_SORT_ORDER)
