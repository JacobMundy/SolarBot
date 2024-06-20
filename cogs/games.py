import discord
from discord.ext import bridge
from discord.ext import commands
from game_logic.dice import DiceView
import random


async def start_dice(ctx: discord.ApplicationContext, sides: int):
    """
    Starts a die roll and responds with the result and appropriate buttons.
    :param ctx:
    :param sides:
    :return:
    """
    view = DiceView(sides=sides, ctx=ctx)
    await view.roll()


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name="roll",
                           description="roll a die",
                           test_guild="1241262568014610482")
    async def roll_die(self, ctx: discord.ApplicationContext, sides: int = 6):
        """
        Rolls a die with the specified number of sides, or 6 by default.
        :param ctx:
        :param sides:
        :return:
        """
        await start_dice(ctx, sides)

    @bridge.bridge_command(name="coinflip",
                           aliases=["cf", "flip"],
                           description="Flip a coin",
                           test_guild="1241262568014610482")
    async def coinflip(self, ctx: discord.ApplicationContext):
        """
        Flips a coin and responds with the result.
        :param ctx:
        :return:
        """
        result = random.choice(["Heads", "Tails"])
        await ctx.respond(f"{result}")


def setup(bot):
    bot.add_cog(Games(bot))
