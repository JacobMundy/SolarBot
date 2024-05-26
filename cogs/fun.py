import random

from discord.ext import commands, bridge


class Responses(commands.Cog):
    def __init__(self, received_bot) -> None:
        self.bot = received_bot

    @bridge.bridge_command(name="ping",
                           description="check the bot's latency",
                           aliases=["pong"],
                           test_guild="1241262568014610482")
    async def ping(self, ctx):
        """
        Responds with the bot's latency.
        :param ctx:
        :return:
        """
        if ctx.invoked_with == "pong":
            await ctx.respond(f'Ping! {round(self.bot.latency * 1000)}ms')
        else:
            await ctx.respond(f'Pong! {round(self.bot.latency * 1000)}ms')

    @bridge.bridge_command(name="greetings",
                           description="greet the bot",
                           aliases=["hello", "hi", "hey", "yo", "sup"],
                           test_guild="1241262568014610482")
    async def greetings(self, ctx):
        """
        Responds with a random greeting.
        :param ctx:
        :return:
        """
        response = random.choice(["Hello!", "Hi!", "Hey!", "Yo!", "Sup!"])
        await ctx.respond(response)


def setup(bot):
    bot.add_cog(Responses(bot))
