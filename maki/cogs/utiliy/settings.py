import discord
from discord.ext import commands

from maki.database.models import Guild


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{type(self).__name__} Cog ready.')

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def prefix(self, ctx, new_prefix: str):
        guild = await Guild.get(ctx.guild.id)
        if guild is None:
            await Guild.create(id=ctx.guild.id, prefix=new_prefix)
        else:
            await guild.update(prefix=new_prefix).apply()
        await ctx.channel.send(f'Changed prefix to {new_prefix}')


def setup(bot):
    bot.add_cog(Settings(bot))
