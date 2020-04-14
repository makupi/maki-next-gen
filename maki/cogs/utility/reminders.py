import re
import time
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from gino import GinoException
from maki.database.models import Reminder
from maki.utils import create_embed, dm_test

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


async def store_reminder(delta, reminder, user_id, channel_id, guild_id, send_dm=False):
    due_time = datetime.now() + delta
    await Reminder.create(due_time=due_time, reminder=reminder, user_id=user_id, channel_id=channel_id,
                          guild_id=guild_id, send_dm=send_dm)


async def reminder_creation(reminder, delta=None):
    embed = await create_embed()
    if delta is None:
        embed.set_footer(text="React with 🗑️ to delete")
        embed.add_field(name="Reminding you about", value=reminder)
    else:
        embed.add_field(name=f'Reminder due in {delta}', value=reminder)
    url = re.search(r"(?P<url>https?://[^\s]+)", reminder)
    if url:
        embed.set_image(url=url.group("url"))
    return embed


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.add_exception_type(GinoException)

    def cog_unload(self):
        self.check_reminders.cancel()

    @tasks.loop(seconds=1.0)
    async def check_reminders(self):
        await self.bot.wait_until_ready()
        due_reminders = await Reminder.query.where(Reminder.due_time > datetime.now()).gino.all()
        for reminder in due_reminders:
            await self.send_reminder(reminder)
            await reminder.delete()

    async def send_reminder(self, reminder):
        embed = await reminder_creation(reminder.reminder)
        user = self.bot.get_user(reminder.user_id)
        if reminder.send_dm:
            msg = await user.send(embed=embed)
        else:
            guild = self.bot.get_guild(reminder.guild_id)
            channel = guild.get_channel(reminder.channel_id)
            msg = await channel.send(f'{user.mention}', embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{type(self).__name__} Cog ready.')
        self.check_reminders.cancel()
        self.check_reminders.start()

    @commands.command()
    async def remindme(self, ctx, _time, *reminder: str):
        delta, reminder, user_id, channel_id, guild_id = parse_reminder(ctx, _time, reminder)
        await store_reminder(delta, reminder, user_id, channel_id, guild_id)
        embed = await reminder_creation(reminder, delta=delta)
        await ctx.send(embed=embed)

    @commands.command()
    async def dmme(self, ctx, _time, *reminder: str):
        if await dm_test(ctx.author):
            delta, reminder, user_id, channel_id, guild_id = parse_reminder(ctx, _time, reminder)
            await store_reminder(delta, reminder, user_id, channel_id, guild_id, send_dm=True)
            embed = await reminder_creation(reminder, delta=delta)
            await ctx.send(embed=embed)
        else:
            embed = await create_embed()
            embed.description = "It seems like I'm not allowed to send you a direct message. \
                                Please follow the steps below to enable direct messages."
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Reminders(bot))
