import asyncio
import re
import time
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from gino import GinoException
from maki.database.models import Reminder
from maki.utils import create_embed, dm_test

UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}

DELETE_EMOTE = "🗑️"


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
        embed.add_field(name="Reminding you about", value=reminder)
    else:
        embed.add_field(name=f'Reminder due in {delta}', value=reminder)
    url = re.search(r"(?P<url>https?://[^\s]+)", reminder)
    if url:
        embed.set_image(url=url.group("url"))
    embed.set_footer(text=f"React with {DELETE_EMOTE}️ to delete")
    return embed


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_reminders())
        self.reaction_queue = dict()

    async def check_reminders(self):
        await self.bot.wait_until_ready()
        while True:
            try:
                due_reminders = await Reminder.query.where(Reminder.due_time < datetime.now()).gino.all()
            except GinoException as ex:
                print(f'GinoException during Reminder.query {ex}')
            else:
                for reminder in due_reminders:
                    await self.send_reminder(reminder)
                    await reminder.delete()
            await asyncio.sleep(1)

    async def send_reminder(self, reminder):
        embed = await reminder_creation(reminder.reminder)
        user = self.bot.get_user(reminder.user_id)
        if reminder.send_dm:
            msg = await user.send(embed=embed)
        else:
            guild = self.bot.get_guild(reminder.guild_id)
            channel = guild.get_channel(reminder.channel_id)
            msg = await channel.send(f'{user.mention}', embed=embed)
        await self.add_delete_logic(msg, user)

    async def add_delete_logic(self, msg, user):
        def check(_reaction, _user):
            return _reaction.message.id == msg.id and _user.id == user.id and _reaction.emoji == DELETE_EMOTE

        self.reaction_queue[msg.id] = check
        await msg.add_reaction(DELETE_EMOTE)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        check = self.reaction_queue.get(reaction.message.id, None)
        if check is not None:
            if user == self.bot.user:
                await self.bot.wait_for("reaction_add", check=check)
                await reaction.message.delete()
                del self.reaction_queue[reaction.message.id]

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{type(self).__name__} Cog ready.')

    @commands.command()
    async def remindme(self, ctx, _time, *reminder: str):
        """: Reminder in the same channel after time expired

                Format: .remindme 1h30m finish this essay

                Ping the author after the time has expired with the given message
                <time> - supports weeks(w) days(d) hours(h) minutes(m) and seconds(s)
                        e.g. 1w2d5h10m45s
                """
        delta, reminder, user_id, channel_id, guild_id = parse_reminder(ctx, _time, reminder)
        await store_reminder(delta, reminder, user_id, channel_id, guild_id)
        embed = await reminder_creation(reminder, delta=delta)
        msg = await ctx.send(embed=embed)
        await self.add_delete_logic(msg, ctx.author)

    @commands.command()
    async def dmme(self, ctx, _time, *reminder: str):
        """: Reminder via direct message after time expired

                Format: .dmme 1h30m finish this essay

                DM the author after the time has expired with the given message
                <time> - supports weeks(w) days(d) hours(h) minutes(m) and seconds(s)
                        e.g. 1w2d5h10m45s
                """
        if await dm_test(ctx.author):
            delta, reminder, user_id, channel_id, guild_id = parse_reminder(ctx, _time, reminder)
            await store_reminder(delta, reminder, user_id, channel_id, guild_id, send_dm=True)
            embed = await reminder_creation(reminder, delta=delta)
            msg = await ctx.send(embed=embed)
        else:
            embed = await create_embed()
            embed.description = "It seems like I'm not allowed to send you a direct message. \
                                Please follow the steps below to enable direct messages."
            msg = await ctx.send(embed=embed)
        await self.add_delete_logic(msg, ctx.author)


def setup(bot):
    bot.add_cog(Reminders(bot))
