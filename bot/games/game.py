import discord
from discord.ext import commands
from bot import database


class Game:
    def __init__(self, ctx: commands.Context, amount: float):
        self.ctx = ctx
        self.amount = amount
        self.user = None

    async def play(self):
        self.user = await database.query_user(self.ctx.author.id, self.ctx.guild.id)
        if not await self.verify_funds():
            await self.send_funds_error()
            return
        reward = await self.game()
        await self.update_funds(reward)

    async def verify_funds(self) -> bool:
        return self.user.balance > self.amount

    async def update_funds(self, reward: float):
        new_balance = self.user.balance - self.amount + reward
        await self.user.update(balance=new_balance).apply()

    async def send_funds_error(self):
        await self.ctx.send(
            embed=discord.Embed(
                description=f"{self.ctx.author.mention} you do not have enough funds to play this game!"
            )
        )

    async def game(self) -> float:
        """game gets called by play automatically
        and is supposed to be implemented by the subclass
        return: amount the play is supposed to be rewarded, without what he put in"""
        pass

    @staticmethod
    def info():
        pass
