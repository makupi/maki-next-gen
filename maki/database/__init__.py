from gino import Gino
from maki.utils import config

db = Gino()


async def setup():
    await db.set_bind(config.database)
