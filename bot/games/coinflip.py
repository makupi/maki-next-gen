import random

import discord

from .game import Game
from bot.utils import format_currency


CHOICES = ["h", "head", "t", "tail"]

CHOICES_STRINGS = {"h": "heads", "t": "tails"}


class CoinFlip(Game):
    def __init__(self, choice: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choice = choice

    def verify_choice(self):
        if self.choice.lower() in CHOICES:
            self.choice = self.choice.lower()[0]
            return True
        return False

    async def send_choice_error(self):
        await self.ctx.send(
            embed=discord.Embed(
                description=f"{self.ctx.author.mention} invalid choice. Possible choices are: `{', '.join(CHOICES)}`."
            )
        )

    async def game(self) -> float:
        if not self.verify_choice():
            await self.send_choice_error()
        win = random.choice(["h", "t"])
        embed = discord.Embed(description=f"🪙 `{CHOICES_STRINGS.get(win)}`\n\n")
        win_amount = 0
        if win == self.choice:
            win_amount = self.amount * 2
            embed.description += (
                f"Nice! You bet {format_currency(self.amount)} on "
                f"`{CHOICES_STRINGS.get(self.choice)}` and won {format_currency(win_amount)}!"
            )
            embed.colour = discord.Colour.green()
        else:
            embed.description += (
                f"Oh no! You bet on `{CHOICES_STRINGS.get(self.choice)}` and lost. "
                f"Good luck next time!"
            )
            embed.colour = discord.Colour.red()
        await self.ctx.send(embed=embed)
        return win_amount
