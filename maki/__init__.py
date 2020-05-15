from pathlib import Path

import discord
import maki.database
from discord.ext import commands
from maki.database.models import Guild
from maki.utils import config

__version__ = "0.1.0"

invite_link = "https://discordapp.com/api/oauth2/authorize?client_id={}&scope=bot&permissions=8192"


async def get_prefix(_bot, message):
    prefix = config.prefix
    if not isinstance(message.channel, discord.DMChannel):
        guild_data = _bot.guild_data.get(message.guild.id, None)
        if guild_data is not None:
            prefix = guild_data.get("prefix", prefix)
    return commands.when_mentioned_or(prefix)(_bot, message)


bot = commands.AutoShardedBot(command_prefix=get_prefix)


async def preload_guild_data():
    guilds = await Guild.query.gino.all()
    d = dict()
    for guild in guilds:
        if guild.prefix:
            d[guild.id] = {"prefix": guild.prefix}
    return d


@bot.event
async def on_ready():
    await database.setup()
    print(
        f"""Logged in as {bot.user}..
        Serving {len(bot.users)} users in {len(bot.guilds)} guilds
        Invite: {invite_link.format(bot.user.id)}
    """
    )
    bot.guild_data = await preload_guild_data()
    await bot.change_presence(activity=discord.Game(f"maki rework v{__version__}"))


def extensions():
    files = Path("maki", "cogs").rglob("*.py")
    for file in files:
        yield file.as_posix()[:-3].replace("/", ".")


def load_extensions(_bot):
    for ext in extensions():
        try:
            _bot.load_extension(ext)
        except Exception as ex:
            print(f"Failed to load extension {ext} - exception: {ex}")


def run():
    load_extensions(bot)
    bot.run(config.token)
