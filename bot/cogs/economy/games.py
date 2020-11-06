import discord
from discord.ext import commands
from bot.games.slots import Slots


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.command()
    async def slots(self, ctx, amount: int = 10):
        """*Gamble with some slots!*

        **Usage**: `{prefix}slots [amount: default 10]`
        **Example**: `{prefix}slots 50`
        """
        game = Slots(ctx, amount)
        await game.play()


def setup(bot):
    bot.add_cog(Games(bot))
