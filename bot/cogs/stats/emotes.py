import re
from collections import Counter

import discord
from discord.ext import commands

from bot.database.models import Emote
from bot.utils import create_embed

EMOTE_REGEX = re.compile(r":[A-Za-z0-9]+:")


def parse_emotes(message: str) -> Counter:
    emotes = EMOTE_REGEX.findall(message)
    emotes = [e.replace(":", "") for e in emotes]
    return Counter(emotes)


async def query_emote(guild_id: int, name: str) -> Emote:
    return (
        await Emote.query.where(Emote.guild_id == guild_id)
        .where(Emote.name == name)
        .gino.first()
    )


async def inc_emote_counters(guild_id: int, emotes: Counter):
    for name, count in emotes.items():
        exists = await query_emote(guild_id, name)
        if exists is None:
            await Emote.create(guild_id=guild_id, name=name, count=count)
        else:
            await exists.update(count=exists.count + count).apply()


class Emotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel) or message.author.bot:
            return
        emotes = parse_emotes(message.content)
        await inc_emote_counters(message.guild.id, emotes)

    @commands.group(invoke_without_command=True, pass_context=True)
    async def emotes(self, ctx):
        print("emotes invoked")

    @emotes.command()
    async def count(self, ctx, *, emote: str):
        """: Show the counter for one or more emotes

        count :emote:
        returns the counter for one or more emotes."""
        emotes = parse_emotes(emote)
        embed = await create_embed(
            description="Current counters for the requested emotes"
        )
        for name in emotes.keys():
            e = await query_emote(ctx.guild.id, name)
            count = 0
            if e is not None:
                count = e.count
            embed.add_field(name=name, value=count, inline=False)
        await ctx.send(embed=embed)

    @emotes.command()
    async def top(self, ctx, amount: int = 5, _filter: str = None):
        """: Shows the top N most used emotes

        You can give an optional amount (N) and filter.
        <amount> - top N emotes
        <filter> - filters emotes with e.g. KEK to find the top KEK emotes
        """
        if amount > 25:
            amount = 25
        query = Emote.query.where(Emote.guild_id == ctx.guild.id)
        if _filter is not None:
            query = query.where(Emote.name.ilike(f"%{_filter}%"))
        emotes = await query.order_by(Emote.count.desc()).limit(amount).gino.all()
        embed = await create_embed()
        if len(emotes) == 0:
            embed.description = "No emote counter found."
            if _filter is not None:
                embed.description = f'No emotes found matching "{_filter}".'
            await ctx.send(embed=embed)
        embed.description = f"Top {len(emotes)} most used emotes"
        if _filter is not None:
            embed.description += f' filtered by "{_filter}"'
        for index, emote in enumerate(emotes):
            embed.add_field(
                name=f"{index+1}. {emote.name}", value=emote.count, inline=False
            )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Emotes(bot))
