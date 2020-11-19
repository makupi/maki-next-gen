import discord

from .config import Config
from .constants import CURRENCY_SYMBOL

config = Config("config.json")


async def dm_test(user):
    try:
        await user.send()
    except discord.Forbidden:
        return False
    except discord.HTTPException:
        return True
    return True


def format_currency(amount: float) -> str:
    return f"{amount:g} {CURRENCY_SYMBOL}"


__all__ = ["config", "dm_test", "format_currency"]
