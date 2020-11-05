import asyncio
import re
from datetime import datetime, timedelta

import aiohttp
import discord
from discord.ext import commands
import webpreview

import bot.database as db
from gino import GinoException
from bot.database.models import Reminder, User
from bot.utils import dm_test

UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}

DELETE_EMOTE = "🗑️"

REGEX_MENTIONS = r"(@everyone|@here|<(?:@!?|@&|#)\d+>)"


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
    due_time = datetime.now().replace(microsecond=0) + delta
    user = await db.query_user(user_id=user_id, guild_id=guild_id)
    await Reminder.create(
        due_time=due_time,
        reminder=reminder,
        user_id=user.id,
        channel_id=channel_id,
        send_dm=send_dm,
    )


async def parse_url_image(url: str):
    try:
        content = None
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.content_type == "text/html":
                    content = await response.content.read()
        og = webpreview.OpenGraph(
            url, properties=["og:image"], content=content, parser="html.parser"
        )
        if og:
            url = og.image
    except Exception as ex:
        print(f"reminder_creation: Fetching of image failed. {ex}")
    return url


async def reminder_creation(reminder, delta=None):
    embed = discord.Embed()
    if delta is None:
        embed.add_field(name="Reminding you about", value=reminder)
    else:
        embed.add_field(name=f"Reminder due in {delta}", value=reminder)
    url = re.search(r"(?P<url>https?://[^\s]+)", reminder)
    if url:
        url = await parse_url_image(url.group("url"))
        embed.set_image(url=url)
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
                due_reminders = await Reminder.query.where(
                    Reminder.due_time < datetime.now()
                ).gino.all()
            except GinoException as ex:
                print(f"GinoException during Reminder.query {ex}")
            else:
                for reminder in due_reminders:
                    await self.send_reminder(reminder)
                    await reminder.delete()
            await asyncio.sleep(1)

    async def send_reminder(self, reminder):
        embed = await reminder_creation(reminder.reminder)
        _user = await User.get(reminder.user_id)
        user = await self.bot.fetch_user(_user.user_id)
        if reminder.send_dm:
            msg = await user.send(embed=embed)
        else:
            channel = self.bot.get_channel(reminder.channel_id)
            msg = await channel.send(f"{user.mention}", embed=embed)
        await self.add_delete_logic(msg, user)

    async def add_delete_logic(self, msg, user):
        def check(_reaction, _user):
            return (
                _reaction.message.id == msg.id
                and _user.id == user.id
                and _reaction.emoji == DELETE_EMOTE
            )

        self.reaction_queue[msg.id] = check
        await msg.add_reaction(DELETE_EMOTE)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        check = self.reaction_queue.get(reaction.message.id, None)
        if check is not None:
            if user == self.bot.user:
                try:
                    await self.bot.wait_for("reaction_add", check=check, timeout=600)
                except asyncio.TimeoutError:
                    await reaction.message.clear_reactions()
                else:
                    await reaction.message.delete()
                del self.reaction_queue[reaction.message.id]

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

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
        msg = await ctx.send(f"{ctx.author.mention}", embed=embed)
        await self.add_delete_logic(msg, ctx.author)
        await ctx.message.delete()

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
            msg = await ctx.send(f"{ctx.author.mention}", embed=embed)
        else:
            embed = discord.Embed()
            embed.description = "It seems like I'm not allowed to send you a direct message. \
                                Please follow the steps below to enable direct messages."
            msg = await ctx.send(embed=embed)
        await self.add_delete_logic(msg, ctx.author)
        await ctx.message.delete()

    @commands.command()
    async def reminders(self, ctx):
        user = await db.query_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        reminders = await Reminder.query.where(Reminder.user_id == user.id).gino.all()
        embed = discord.Embed()
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        if len(reminders) == 0:
            embed.description = "You don't have any active reminders right now!"
        for reminder in reminders:
            due = reminder.due_time - datetime.now().replace(microsecond=0)
            embed.add_field(
                name=f"#{reminder.id} due in {due}",
                value=reminder.reminder,
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(
        name="cancel-reminder",
        aliases=["cancel_reminder", "cancelReminder", "cancelreminder"],
    )
    async def cancel_reminder(self, ctx, number: int):
        user = await db.query_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        reminder = await Reminder.get(number)
        embed = discord.Embed()
        if reminder is None:
            embed.description = f"Reminder **#{number}** not found!"
        else:
            due = reminder.due_time - datetime.now().replace(microsecond=0)
            if user.id == reminder.user_id:
                embed.description = f"Cancelled reminder **#{reminder.id}** with {due} left."
                await reminder.delete()
            else:
                embed.description = (
                    "You are not the creator of this reminder. You cannot delete it!"
                )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Reminders(bot))
