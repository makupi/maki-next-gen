import discord
import bot.database as db
from discord.ext import commands
from bot.database.models import Guild


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        _ = await db.query_guild(guild.id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            _ = await db.query_user(user_id=member.id, guild_id=member.guild.id)

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def prefix(self, ctx, new_prefix: str):
        """*Change your servers prefix*
        **Example**: `{prefix}prefix !`
        **Requires permission**: `MANAGER SERVER`
        """
        embed = discord.Embed(description="Prefix changed")
        guild = await Guild.get(ctx.guild.id)
        if guild is None:
            await Guild.create(id=ctx.guild.id, prefix=new_prefix)
            self.bot.guild_data[ctx.guild.id] = {"prefix": new_prefix}
        else:
            embed.add_field(
                name="From", value=("Not set" if guild.prefix is None else guild.prefix)
            )
            await guild.update(prefix=new_prefix).apply()
            self.bot.guild_data[ctx.guild.id].update({"prefix": new_prefix})

        embed.add_field(name="To", value=new_prefix)
        await ctx.channel.send(embed=embed)

    @prefix.error
    async def prefix_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description="Sorry, you need `MANAGE SERVER` permission to change the prefix!"
                )
            )


def setup(bot):
    bot.add_cog(Settings(bot))
