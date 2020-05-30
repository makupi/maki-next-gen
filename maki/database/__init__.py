from gino import Gino
from maki.utils import config

db = Gino()

# import models so Gino registers them
import maki.database.models as models  # isort:skip


async def setup():
    await db.set_bind(config.database)


async def shutdown():
    await db.pop_bind().close()


async def query_user(user_id: int, guild_id: int):
    """: query user, create if not exist"""
    user = (
        await models.User.query.where(models.User.guild_id == guild_id)
        .where(models.User.user_id == user_id)
        .gino.first()
    )
    if user is None:
        user = await models.User.create(user_id=user_id, guild_id=guild_id)
    return user


async def query_guild(guild_id: int):
    """: query guild, create if not exist"""
    guild = await models.Guild.get(guild_id)
    if guild is None:
        guild = await models.Guild.create(id=guild_id)
    return guild
