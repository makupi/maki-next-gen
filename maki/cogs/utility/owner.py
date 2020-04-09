import subprocess
import sys

import discord
from discord.ext import commands

import maki.database as db
from maki.utils import config


def fix_cog_path(cog):
    if not cog.startswith('maki.cogs.'):
        if not cog.startswith('cogs.'):
            return 'maki.cogs.'+cog
        return 'maki.'+cog
    return cog


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
        old_prefix = config.prefix
        config.prefix = new_prefix
        config.store()
        embed = discord.Embed(title='Changing default prefix')
        embed.add_field(name='From', value=old_prefix)
        embed.add_field(name='To', value=new_prefix)
        await ctx.send(embed=embed)

    @commands.command()
    async def shutdown(self, ctx):
        await db.shutdown()
        await ctx.send(embed=discord.Embed(title='Shutting down..'))

        sys.exit()

    @commands.command()
    async def load(self, ctx, cog: str):
        embed = discord.Embed(title=f'Load Extension {cog}')
        try:
            self.bot.load_extension(fix_cog_path(cog))
        except (commands.ExtensionAlreadyLoaded, commands.ExtensionNotFound) as ex:
            embed.add_field(name='Error', value=f'{type(ex).__name__} - {ex}')
        else:
            embed.description = 'Success'
        await ctx.send(embed=embed)

    @commands.command()
    async def unload(self, ctx, cog: str):
        embed = discord.Embed(title=f'Unload Extension {cog}')
        try:
            self.bot.unload_extension(fix_cog_path(cog))
        except commands.ExtensionNotLoaded as ex:
            embed.add_field(name='Error', value=f'{type(ex).__name__} - {ex}')
        else:
            embed.description = 'Success'
        await ctx.send(embed=embed)

    @commands.command()
    async def reload(self, ctx, cog: str):
        embed = discord.Embed(title=f'Reload Extension {cog}')
        try:
            self.bot.reload_extension(fix_cog_path(cog))
        except (commands.ExtensionNotLoaded, commands.ExtensionNotFound) as ex:
            embed.add_field(name='Error', value=f'{type(ex).__name__} - {ex}')
        else:
            embed.description = 'Success'
        await ctx.send(embed=embed)

    @commands.command()
    async def cogs(self, ctx):
        msg = ''
        for cog in self.bot.cogs:
            msg += f"- {cog}\n"
        await ctx.send(embed=discord.Embed(title='Loaded Extensions', description=msg))

    @commands.command()
    async def exec(self, ctx, *command: str):
        embed = discord.Embed(title=' '.join(command))
        try:
            with subprocess.Popen(
                    [*list(command)], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as proc:
                out = proc.stdout.read().decode()[0:1994]  # max 2000 signs per message
                err = proc.stderr.read().decode()[0:1994]
                if out:
                    embed.add_field(name='stdout', value=out)
                if err:
                    embed.add_field(name='stderr', value=out)
        except Exception as ex:
            embed.add_field(name='Exception', value=str(ex))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Owner(bot))
