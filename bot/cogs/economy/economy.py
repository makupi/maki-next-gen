from datetime import datetime, timedelta

import discord
from discord.ext import commands

import bot.database as db

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
        embed = discord.Embed()
        day_ago = datetime.now().replace(microsecond=0) - timedelta(hours=24)
        if user.last_daily is not None and user.last_daily > day_ago:
            delta = user.last_daily - day_ago
            embed.description = f"Daily is on cooldown for you! You can use it again in {delta}."
        else:
            if user.balance is None:
                user.balance = 0
            user.balance += DAILY_INCREASE
            # TODO: check for daily streak
            user.last_daily = datetime.now().replace(microsecond=0)
            await user.update(balance=user.balance, last_daily=user.last_daily).apply()
            embed.description = (
                f"You have gained {DAILY_INCREASE}. Your new balance is now {user.balance}."
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def balance(self, ctx):
        user = await db.query_user(user_id=ctx.author.id, guild_id=ctx.guild.id)
        if user.balance is None:
            user.balance = 0
            await user.update(balance=user.balance).apply()
        embed = discord.Embed(description=f"Your current balance is: {user.balance}.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))
