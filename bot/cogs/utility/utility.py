import sys
import time
from datetime import datetime

import discord
from discord.ext import commands
from bot import utils

PY_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now().replace(microsecond=0)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed()
        before_time = time.time()
        msg = await ctx.send(embed=embed)
        latency = round(self.bot.latency * 1000)
        elapsed_ms = round((time.time() - before_time) * 1000) - latency
        embed.add_field(name="ping", value=f"{elapsed_ms}ms")
        embed.add_field(name="latency", value=f"{latency}ms")
        await msg.edit(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        current_time = datetime.now().replace(microsecond=0)
        embed = discord.Embed(
            description=f"Time since I went online: {current_time - self.start_time}."
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def starttime(self, ctx):
        embed = discord.Embed(description=f"I'm up since {self.start_time}.")
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(title="Maki")
        embed.url = "https://top.gg/bot/431485759304892416"
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(
            name="Bot Stats",
            value=f"```py\n"
            f"Guilds: {len(self.bot.guilds)}\n"
            f"Users: {len(self.bot.users)}\n"
            f"Shards: {self.bot.shard_count}\n"
            f"Shard ID: {ctx.guild.shard_id}```",
            inline=False,
        )
        embed.add_field(
            name=f"Server Configuration",
            value=f"```\n" f"Prefix: {utils.config.prefix}\n" f"```",
            inline=False,
        )
        embed.add_field(
            name="Activity",
            value=f"```py\n"
            f"Processing {self.bot.active_commands} commands\n"
            f"{self.bot.total_commands} commands since startup```",
        )
        embed.add_field(
            name="Software Versions",
            value=f"```py\n"
            f"Maki: {self.bot.version}\n"
            f"discord.py: {discord.__version__}\n"
            f"Python: {PY_VERSION}```",
            inline=False,
        )
        embed.add_field(
            name="Links",
            value=f"[Invite]({self.bot.invite}) | "
            f"[Vote](https://top.gg/bot/431485759304892416/vote) | "
            f"[Support](https://discord.gg/vU7pDXB) | "
            f"[Ko-fi](https://ko-fi.com/makubob) | "
            f"[Github](https://github.com/makupi) | "
            f"[Twitter](https://twitter.com/makubob)",
            inline=False,
        )
        embed.set_footer(text="Thank you for using maki <3", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["socials", "invite", "support"])
    async def links(self, ctx):
        embed = discord.Embed()
        embed.description = (
            f"[Invite]({self.bot.invite}) | "
            f"[Vote](https://top.gg/bot/431485759304892416/vote) | "
            f"[Support](https://discord.gg/vU7pDXB) | "
            f"[Ko-fi](https://ko-fi.com/makubob) | "
            f"[Github](https://github.com/makupi) | "
            f"[Twitter](https://twitter.com/makubob)"
        )
        embed.set_footer(text="Thank you for using maki <3", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
