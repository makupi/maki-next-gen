import aiohttp
import discord
from discord.ext import commands

from maki.utils import config, create_embed

API = "http://www.omdbapi.com/"


class IMDb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = config.omdb_key

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    async def _fetch_json(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}&apikey={self.api_key}") as r:
                    return await r.json()
        except aiohttp.ClientError:
            return None

    @commands.command()
    async def movie(self, ctx, *, movie: str):
        url = f"{API}?s={movie}"
        data = await self._fetch_json(url)
        embed = await create_embed()
        if data is None:
            embed.description = "No matching movie found, please try again!"
            await ctx.send(embed=embed)
            return
        search = data.get("Search")
        msg = None
        movie_id = None
        if len(search) > 1:
            movies = dict()
            desc = "*Please pick a movie*\n\n"
            for index, movie in enumerate(search):
                emote = str(index) + "⃣"
                movies[emote] = movie.get("imdbID")
                desc += f"{emote} {movie.get('Title')} ({movie.get('Year')})\n"
            embed.description = desc
            msg = await ctx.send(embed=embed)
            for emote in movies.keys():
                await msg.add_reaction(emote)

            def check(reaction, user):
                return (
                    reaction.message.id == msg.id
                    and user == ctx.message.author
                    and reaction.emoji in movies
                )

            reaction, user = await self.bot.wait_for(
                "reaction_add", check=check, timeout=360
            )
            movie_id = movies[reaction.emoji]
            await msg.clear_reactions()
            embed = await create_embed()
        elif len(search) == 1:
            movie_id = search[0].get("imdbID")
        if movie_id:
            url = f"{API}?i={movie_id}"
            data = await self._fetch_json(url)
            print(data)


def setup(bot):
    bot.add_cog(IMDb(bot))
