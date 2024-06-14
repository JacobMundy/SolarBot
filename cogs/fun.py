import random

import discord
from discord.ext import commands, bridge


class Responses(commands.Cog):
    def __init__(self, received_bot):
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


    @bridge.bridge_command(name="magic8ball",
                           aliases=["8ball", "8b", "m8ball", "eightball"],
                           description="ask the magic 8 ball a question",
                           test_guild="1241262568014610482")
    async def magic8ball(self, ctx, *, question):
        """
        Responds with a random magic 8-ball response.
        :param ctx:
        :param question:
        :return:
        """
        # responses https://en.wikipedia.org/wiki/Magic_8_Ball#Possible_answers
        affirmative = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes definitely.",
                       "You may rely on it", "As I see it yes", "Most likely", "Outlook good", "Yes",
                       "Signs point to yes"]
        non_committal = ["Reply hazy, try again", "Ask again later", "Better not tell you now",
                         "Cannot predict now", "Concentrate and ask again"]
        negative = ["Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]

        response = random.choice(affirmative + non_committal + negative)

        embed = discord.Embed(title="Magic 8 Ball :8ball:",
                              color=discord.Color.blurple())
        embed.add_field(name="Question:", value=question, inline=False)
        embed.add_field(name="Answer:", value=response, inline=False)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Responses(bot))
