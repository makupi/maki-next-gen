import discord
from discord.ext import commands
import maki.utils

__version__ = "0.0.1"

config = utils.Config("config.json")

invite_link = "https://discordapp.com/api/oauth2/authorize?client_id={}&scope=bot"


def get_prefix(_bot, message):
    prefix = config.prefix
    if not isinstance(message.channel, discord.DMChannel):
        pass  # query guild-prefix
    return commands.when_mentioned_or(prefix)(_bot, message)


bot = commands.AutoShardedBot(command_prefix=get_prefix)


@bot.event
async def on_ready():
    print(f'''Logged in as {bot.user}..
        Serving {len(bot.users)} users in {len(bot.guilds)}.
        Invite: {invite_link.format(bot.user.id)}
    ''')

def run():
    bot.run(config.token)