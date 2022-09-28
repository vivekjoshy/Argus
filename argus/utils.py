from discord import Interaction


async def update(interaction: Interaction, *args, **kwargs):
    """
    Convenience method that updates an initial response if one is already sent.
    If no initial response is sent, then it sends one.
    """
    if interaction.response.is_done():
        if "ephemeral" in kwargs:
            kwargs.pop("ephemeral")
        await interaction.edit_original_response(*args, **kwargs)
    else:
        await interaction.response.send_message(*args, **kwargs)


def floor_rating(rating_input: float) -> float:
    """
    Returns the closest value for a rating role's value.
    """
    ratings = [
        1333 + 1 / 3,
        1250,
        1166 + 2 / 3,
        1083 + 1 / 3,
        1000,
        583 + 1 / 3,
        500,
        416 + 2 / 3,
        83 + 1 / 3,
        0,
    ]
    rating_counter = 0
    for rating in ratings[::-1]:
        if rating_input >= rating:
            rating_counter = rating

    if rating_counter > 0:
        return rating_counter
    else:
        return 0


def normalize(d: dict, target=1.0):
    """
    Normalize a dictionary's values to the target value.
    """
    raw = sum(d.values())
    if raw == 0:
        factor = target / 1
    else:
        factor = target / raw
    return {key: value * factor for key, value in d.items()}
