import re
import time
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from maki.database.models import Reminder

UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}


def convert_to_delta(_time):
    _unit = {}
    for t in _time:
        count = int(t[:-1])
        unit = UNITS[t[-1]]
        _unit[unit] = count
    td = timedelta(**_unit)
    return td


def parse_reminder(ctx, _time, reminder):
    user_id = ctx.author.id
    guild_id = None
    if ctx.guild is not None:
        guild_id = ctx.guild.id
    channel_id = ctx.channel.id
    reminder = " ".join(reminder)
    regex = r"([0-9]+[smhdw])"
    _time = re.findall(regex, str(_time))
    due_time = convert_to_delta(_time)
    return due_time, reminder, user_id, channel_id, guild_id


async def store_reminder(due_time, reminder, user_id, channel_id, guild_id, send_dm=False):
    due_time = datetime.now() + due_time
    await Reminder.create(due_time=due_time, reminder=reminder, user_id=user_id, channel_id=channel_id, guild_id=guild_id, send_dm=send_dm)

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{type(self).__name__} Cog ready.')

    @commands.command()
    async def remindme(self, ctx, _time, *reminder: str):
        await store_reminder(*parse_reminder(ctx, _time, reminder))

    @commands.command()
    async def dmme(self, ctx, _time, *reminder: str):
        await store_reminder(*parse_reminder(ctx, _time, reminder), send_dm=True)


def setup(bot):
    bot.add_cog(Reminders(bot))
