import asyncio
import re
from datetime import datetime

import discord
from discord.ext import commands

import bot.database as db
from gino import GinoException
from bot.cogs.utility.reminders import convert_to_delta
from bot.database.models import Poll
from bot.utils import create_embed

EMOTE_BOX = "⃣"

EMOTE_LIST = [
    "1" + EMOTE_BOX,
    "2" + EMOTE_BOX,
    "3" + EMOTE_BOX,
    "4" + EMOTE_BOX,
    "5" + EMOTE_BOX,
    "6" + EMOTE_BOX,
    "7" + EMOTE_BOX,
    "8" + EMOTE_BOX,
    "9" + EMOTE_BOX,
]


def parse_timedelta(_time):
    regex = r"([0-9]+[smhdw])"
    _time = re.findall(regex, str(_time))
    due_time = convert_to_delta(_time)
    return due_time


class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_polls())

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    async def check_polls(self):
        await self.bot.wait_until_ready()
        while True:
            try:
                due_polls = await Poll.query.where(
                    Poll.due_time < datetime.now()
                ).gino.all()
            except GinoException as ex:
                print(f"GinoException during Reminder.query {ex}")
            else:
                for poll in due_polls:
                    await self.send_results(poll)
                    await poll.delete()
            await asyncio.sleep(1)

    async def send_results(self, poll: Poll):
        channel = self.bot.get_channel(poll.channel_id)
        msg = await channel.fetch_message(poll.message_id)
        title = ""
        for embed in msg.embeds:
            title = embed.title

        embed = await create_embed(title=title)
        votes = dict()
        for reaction in msg.reactions:
            if reaction.emoji in EMOTE_LIST:
                option = poll.options[EMOTE_LIST.index(reaction.emoji)]
                votes[option] = reaction.count - 1
        sorted_votes = {
            k: v
            for k, v in sorted(votes.items(), key=lambda item: item[1], reverse=True)
        }
        desc = "📊 **Results**\n"
        for k, v in sorted_votes.items():
            desc += f"**{v}** votes for {k}\n"
        embed.description = desc
        await channel.send(embed=embed)

    @commands.command()
    async def poll(self, ctx, time, question, *options):
        embed = discord.Embed(title=question)
        desc = ""
        options_dict = dict()
        for index, option in enumerate(options):
            emote = EMOTE_LIST[index]
            desc += f"{emote} {option}\n"
            options_dict[emote] = option
        embed.description = desc
        due_time = datetime.now().replace(microsecond=0) + parse_timedelta(time)
        embed.timestamp = datetime.utcnow().replace(microsecond=0) + parse_timedelta(
            time
        )
        embed.set_footer(text="Due ")
        msg = await ctx.send(embed=embed)
        for emote in options_dict.keys():
            await msg.add_reaction(emote)
        user = await db.query_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        await Poll.create(
            creator_id=user.id,
            due_time=due_time,
            channel_id=ctx.channel.id,
            message_id=msg.id,
            options=options,
        )


def setup(bot):
    bot.add_cog(Polls(bot))
