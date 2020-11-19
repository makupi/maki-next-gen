import discord
from discord.ext import commands
from bot import games


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.command()
    async def slots(self, ctx, amount: float = 10.0):
        """*Gamble with some slots!*

        **Usage**: `{prefix}slots [amount: default 10]`
        **Example**: `{prefix}slots 50`
        """
        game = games.Slots(ctx, amount)
        await game.play()

    @commands.command()
    async def coinflip(self, ctx, choice: str, amount: float = 10.0):
        """*Flip a coin!*

        **Usage**: `{prefix}coinflip <choice> [amount: default 10]`
        <choice>: either `head` or `tail` or simply `h` or `t`
        **Example**: `{prefix}coinflip h 25`
        """
        game = games.CoinFlip(choice, ctx, amount)
        await game.play()


def setup(bot):
    bot.add_cog(Games(bot))
