import asyncio

import bot.database as db
from bot.database.models import Emote, Guild, Reminder

from .database_transfer import from_emotes_data, from_reminder_data, guild_config_transfer, setup


async def transfer_database():
    await setup()
    # await asyncio.sleep(10)
    # await transfer_guilds()
    # await transfer_emotes()
    await transfer_reminders()


async def transfer_guilds():
    print(f"transferring {len(guild_config_transfer)} guilds..")
    # await Guild.delete.gino.all()
    # await asyncio.sleep(5)
    for k, v in guild_config_transfer.items():
        print(f"transfering {k}:{v} .. ")
        guild = await Guild.get(k)
        if guild is None:
            await Guild.create(id=k, prefix=v)
        else:
            await guild.update(prefix=v).apply()


async def transfer_emotes():
    # print(f"transferring {len(from_emotes_data)} emotes..")
    await Emote.delete.gino.all()
    await asyncio.sleep(5)
    for emote in from_emotes_data:
        guild_id = emote.get("guildId")
        emotes = emote.get("emotes")
        print(f"transferring {len(emotes)} emotes from guild {guild_id}.. ")
        for e in emotes:
            name = e.get("name")
            count = e.get("count")
            # exists = (
            #     await Emote.query.where(Emote.guild_id == guild_id)
            #     .where(Emote.name == name)
            #     .gino.first()
            # )
            # if exists is None:
            await Emote.create(guild_id=guild_id, name=name, count=count)
            # else:
            #     await exists.update(count=count).apply()


async def transfer_reminders():
    # print(f"transferring {len(from_reminder_data)} reminders..")
    await Reminder.delete.gino.all()
    await asyncio.sleep(5)
    for reminder in from_reminder_data:
        due_time = reminder.get("dueTime")
        note = reminder.get("note")
        user_id = reminder.get("userId")
        channel_id = reminder.get("channelId")
        guild_id = reminder.get("guildId")
        send_dm = reminder.get("sendDM")
        user = await db.query_user(user_id=user_id, guild_id=guild_id)
        await Reminder.create(
            due_time=due_time,
            reminder=note,
            user_id=user.id,
            channel_id=channel_id,
            send_dm=send_dm,
        )


def run_transfer():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(transfer_database())
