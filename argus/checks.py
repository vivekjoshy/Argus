from discord import Interaction, app_commands

from argus.errors import UnsatisfiedRequirements


def check_prerequisites_enabled():
    """
    Checks if the server pre-requisites are satisfied.
    """

    def predicate(interaction: Interaction) -> bool:
        guild = interaction.guild
        if (
            "COMMUNITY" in guild.features
            and guild.public_updates_channel
            and guild.rules_channel
        ):
            return True
        else:
            raise UnsatisfiedRequirements(
                "Please enable the community features such as the rules and public updates channels."
            )

    return app_commands.check(predicate)
