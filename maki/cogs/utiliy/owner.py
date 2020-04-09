import sys

import discord
from discord.ext import commands

import maki.database as db
from maki.utils import config


class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)
 
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{type(self).__name__} Cog ready.')

    @commands.command()
    async def defaultprefix(self, ctx, new_prefix: str):
        config.prefix = new_prefix
        config.store()

    @commands.command()
    async def shutdown(self, ctx):
        await db.shutdown()
        await ctx.channel.send('Shutting down..')

        sys.exit()


def setup(bot):
    bot.add_cog(Owner(bot))
