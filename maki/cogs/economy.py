import discord
from discord.ext import commands

import maki.database as db


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.command()
    async def daily(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Economy(bot))
