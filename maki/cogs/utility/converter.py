import re
import string

from discord.ext import commands

from maki.utils import create_embed
from pint import UnitRegistry
from pint.errors import DimensionalityError

ureg = UnitRegistry()
Q_ = ureg.Quantity

UNITS = {
    "k": ureg.kelvin,
    "c": ureg.degC,
    "f": ureg.degF,
    "m": ureg.meter,
    "mi": ureg.mile,
    "cm": ureg.centimeter,
    "mm": ureg.millimeter,
    "km": ureg.kilometer,
    "nmi": ureg.nautical_mile,
    "ft": ureg.foot,
    "in": ureg.inch,
    "yd": ureg.yard,
    "kph": (ureg.kilometer / ureg.hour),
    "kt": ureg.knot,
    "kps": (ureg.kilometer / ureg.second),
    "mps": (ureg.meter / ureg.second),
    "mph": (ureg.mile / ureg.hour),
    "l": ureg.litre,
    "ml": ureg.millilitre,
    "cl": ureg.centilitre,
    "dl": ureg.decilitre,
    "floz": ureg.floz,
    "kg": ureg.kilogram,
    "lb": ureg.pound,
    "g": ureg.gram,
    "oz": ureg.ounce,
    "sv": ureg.sievert,
    "usv": ureg.microsievert,
    "gy": ureg.gray,
    "ugy": ureg.microgray,
    "rem": ureg.rem,
    "rads": ureg.rads,
}


class UnitUnknown(Exception):
    pass


class InvalidParameters(Exception):
    pass


def parse_input_parameters(value, unit, dummy, new_unit):
    if new_unit is None:
        if dummy in UNITS:
            new_unit = dummy
        if dummy is None or unit == "to":
            try:
                _ = float(value)
            except ValueError:
                regex = r"(?P<Numeric>[0-9]*)(?P<Alpha>[a-zA-Z]*)"
                search = re.search(regex, value)
                _value = search.group("Numeric")
                _unit = search.group("Alpha")
                if _unit in UNITS:
                    if unit in UNITS:
                        new_unit = unit
                    value = _value
                    unit = _unit
            else:
                raise InvalidParameters
    pint_unit = UNITS.get(unit, None)
    if pint_unit is None:
        raise UnitUnknown(unit)
    pint_new_unit = UNITS.get(new_unit, None)
    if pint_new_unit is None:
        raise UnitUnknown(new_unit)
    pint_value = Q_(float(value), pint_unit)
    return pint_value, pint_unit, pint_new_unit


class Converter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.command()
    async def convert(self, ctx, value=None, unit=None, dummy=None, new_unit=None):
        """: Converts between given units."""
        embed = await create_embed(title="Conversion Failed")
        try:
            if value is None:
                raise InvalidParameters
            value, unit, new_unit = parse_input_parameters(value, unit, dummy, new_unit)
        except UnitUnknown as ex:
            embed.description = (
                f"Unit `{ex}` unknown. "
                f"Please check the `units` command for available units."
            )
        except InvalidParameters:
            embed.description = (
                "Received Invalid Parameters. Please use the following format: "
                "\n - `convert VALUE UNIT to NEW_UNIT`\n - `convert 1 km to mi`"
            )
        else:
            try:
                new_value = value.to(new_unit)
            except DimensionalityError:
                embed.description = (
                    f"Conversion from `{unit}` to `{new_unit}` not possible."
                )
            else:
                embed.title = ""
                embed.description = f"{value:.3f} is equal to {new_value:.3f}"
        await ctx.send(embed=embed)

    @commands.command()
    async def units(self, ctx):
        """: List of possible units for conversion."""
        tmp = "```"
        for unit_abr, unit in UNITS.items():
            tmp += f"{unit_abr:4s} - {string.capwords(str(unit))}\n"
        tmp += "```"
        tmp = tmp.replace("Degree_fahrenheit", "Fahrenheit")
        tmp = tmp.replace("Degree_celsius", "Celsius")
        tmp = tmp.replace("Nautical_mile", "Nautical Mile")

        embed = await create_embed(
            title="Supported Units for Conversion", description=tmp
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Converter(bot))
