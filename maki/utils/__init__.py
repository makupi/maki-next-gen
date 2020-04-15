import discord

from .config import Config
from .embeds import create_embed

config = Config("config.json")


async def dm_test(user):
    try:
        await user.send()
    except discord.Forbidden:
        return False
    except discord.HTTPException:
        return True
    return True
