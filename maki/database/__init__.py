from gino import Gino
from maki.utils import config


db = Gino()

# import models so Gino registers them
import maki.database.models  # isort:skip


async def setup():
    await db.set_bind(config.database)
