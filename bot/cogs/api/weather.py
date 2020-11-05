from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

from bot.utils import config

API = "https://api.openweathermap.org/data/2.5/weather?units=metric"


def get_icon_url(icon_id):
    return f"http://openweathermap.org/img/wn/{icon_id}@2x.png"


def c_to_f(c):
    return round((c * 9 / 5) + 32, 2)


def kmh_to_mph(kmh):
    return round((1.609344 * kmh), 2)


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = config.owm_key

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    async def _fetch_json(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}&appid={self.api_key}") as r:
                    return await r.json()
        except aiohttp.ClientError:
            return None

    @commands.command()
    async def weather(self, ctx, *, location: str):
        url = f"{API}&q={location}"
        data = await self._fetch_json(url)
        cod = data.get("cod")
        if data is None or cod == "429":
            embed = discord.Embed(description="Something went wrong, please try again later!")
            await ctx.send(embed=embed)
            if cod == "429":
                await self.notify_owner()
            return
        if cod == "404":
            embed = discord.Embed(description=f"Location `{location}` not found!")
            await ctx.send(embed=embed)
            return
        w = data.get("weather")[0]
        desc = w.get("description")
        icon_url = get_icon_url(w.get("icon"))
        main = data.get("main")
        temp = main.get("temp")
        feels_like = main.get("feels_like")
        humidity = main.get("humidity")
        wind = data.get("wind")
        wind_speed = wind.get("speed")
        sys = data.get("sys")
        country = sys.get("country")
        sunrise = datetime.fromtimestamp(sys.get("sunrise"))
        str_sunrise = sunrise.strftime("%H:%M")
        sunset = datetime.fromtimestamp(sys.get("sunset"))
        str_sunset = sunset.strftime("%H:%M")
        name = data.get("name")
        loc = f"{name}, {country}"

        embed = discord.Embed(title=loc, description="*current weather*")
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(text="Powered by openweathermap.org")
        embed.timestamp = datetime.utcnow()
        embed.add_field(name="Avg. Temp", value=f"{temp}°C / {c_to_f(temp)}°F")
        embed.add_field(name="Weather", value=desc.capitalize())
        embed.add_field(name="Humidity", value=f"{humidity}%")

        embed.add_field(name="Feels like", value=f"{feels_like}°C / {c_to_f(feels_like)}°F")
        embed.add_field(name="Wind speed", value=f"{wind_speed} kmh / {kmh_to_mph(wind_speed)} mph")
        embed.add_field(name="\u200c", value="\u200c")

        embed.add_field(name="Sunrise", value=str_sunrise)
        embed.add_field(name="Sunset", value=str_sunset)
        embed.add_field(name="\u200c", value="\u200c")

        await ctx.send(embed=embed)

    async def notify_owner(self):
        appinfo = await self.bot.application_info()
        await appinfo.owner.send("looks like openweathermap.org rate limit might have exceeded!")


def setup(bot):
    bot.add_cog(Weather(bot))
