import discord
from discord.ext import commands
from maki.utils import config


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{type(self).__name__} Cog ready.')

    @commands.is_owner()
    @commands.command()
    async def defaultprefix(self, ctx, new_prefix: str):
        config.prefix = new_prefix
        config.store()


def setup(bot):
    bot.add_cog(Owner(bot))
