import discord
import os
from discord.ext import bridge

# Add any cogs you want to load here,
# should be names of the files in the cogs directory
cogs_list = ['banking',
             'games',
             'fun',
             'admin']

bot = bridge.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.listen()
async def on_message(message):

    if message.author == bot.user or len(message.content) == 0:
        return

    print(f"Message sent in channel {message.channel}")
    if message.content[0] == "!":
        print(f"Command detected: {message.content}")


def run_bot():
    for cog in cogs_list:
        bot.load_extension(f"cogs.{cog}")
    token = str(os.getenv("DISCORD_TOKEN"))
    bot.run(token)
