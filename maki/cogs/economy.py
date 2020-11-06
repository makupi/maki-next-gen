from datetime import datetime, timedelta

import discord
from discord.ext import commands

import maki.database as db
from maki.utils import create_embed

DAILY_INCREASE = 50


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.command()
    async def daily(self, ctx):
        user = await db.query_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        embed = await create_embed()
        day_ago = datetime.now().replace(microsecond=0) - timedelta(hours=24)
        if user.last_daily is not None and user.last_daily > day_ago:
            delta = user.last_daily - day_ago
            embed.description = f"Daily is on cooldown for you! You can use it again in {delta}."
        else:
            if user.money is None:
                user.money = 0
            user.money += DAILY_INCREASE
            # TODO: check for daily streak
            user.last_daily = datetime.now().replace(microsecond=0)
            await user.update(money=user.money, last_daily=user.last_daily).apply()
            embed.description = (
                f"You have gained {DAILY_INCREASE}. Your new balance is now {user.money}."
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def balance(self, ctx):
        user = await db.query_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        if user.money is None:
            user.money = 0
            await user.update(money=user.money).apply()
        embed = await create_embed(description=f"Your current balance is: {user.money}.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))
