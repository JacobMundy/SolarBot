import discord
import os

from discord.ext import bridge
from cogs.banking import Banking
from cogs.games import Games


bot = bridge.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.command(name="hello",
             description="say hello",
             test_guild="1241262568014610482")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hello!")


@bot.listen()
async def on_message(message):

    if message.author == bot.user or len(message.content) == 0:
        return

    print(f"Message sent in channel {message.channel}")
    if message.content[0] == "!":
        print(f"Command detected: {message.content}")
        # await responses.handle_response(message, bot)


def run_bot():
    bot.add_cog(Banking(bot))
    bot.add_cog(Games(bot))
    token = str(os.getenv("DISCORD_TOKEN"))
    bot.run(token)
