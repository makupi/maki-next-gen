import io
import json
from typing import Optional

import aiohttp
import discord
from discord.ext import commands
from bot.utils import config


class Colors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_api = config.maki_api

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    async def _fetch_image(self, endpoint: str, data: dict) -> Optional[discord.File]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_api}{endpoint}", data=json.dumps(data)) as r:
                    if r.status != 200:
                        return None
                    b = await r.read()
                    image = io.BytesIO(b)
                    image.seek(0)
                    return discord.File(filename="image.png", fp=image)
        except aiohttp.ClientError:
            return None

    async def send_api_image(self, ctx: commands.Context, endpoint: str, data: dict):
        image = await self._fetch_image(endpoint, data)
        if image is not None:
            return await ctx.send(file=image)
        await ctx.send(f"Something went wrong. Please try again.")

    @commands.command()
    async def color(self, ctx: commands.Context, color: str):
        """*Display a single color*

        **Usage**: {prefix}color <color-code>
        **Example**: {prefix}color #FF80AA
        """
        await self.send_api_image(ctx, "/square", {"color": color})

    @commands.command()
    async def palette(self, ctx: commands.Context, *, colors: str):
        """*Display a multiple colors as a palette*

        You can enter as many colors as you wish!
        **Usage**: {prefix}palette <color1> <color2> <color3> ..
        **Example**: {prefix}palette #112233 #445566 #778899
        """
        colors = colors.split(" ")
        await self.send_api_image(ctx, "/palette", {"colors": colors, "label": False})


def setup(bot):
    bot.add_cog(Colors(bot))
