import json

from bot.database import db
from pymongo import MongoClient

with open("tools/transfer.json") as file:
    data = json.load(file)
    from_database_url = data.get("from")
    to_database_url = data.get("to")
    db_name = data.get("fromDB")


_from_db = MongoClient(from_database_url)
from_db = _from_db[db_name]
emotes = from_db.emotes
servers = from_db.servers
reminders = from_db.reminders

from_servers_data = servers.find()
guild_config_transfer = dict()

for server in from_servers_data:
    guild_id = server.get("guildId")
    prefix = server.get("config").get("prefix")
    if guild_id is not None and prefix is not None:
        guild_config_transfer[guild_id] = prefix
#  print(f"{len(guild_config_transfer)} entries to be transfered for guild_config")

from_emotes_data = emotes.find()
from_reminder_data = reminders.find()


async def setup():
    await db.set_bind(to_database_url)
    await db.gino.create_all()


async def shutdown():
    await db.pop_bind().close()
