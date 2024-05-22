import random
import discord
import os

import blackjack
import responses
from dice import DiceView

bot = discord.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.slash_command(name="blackjack",
                   description="play a game of blackjack",
                   test_guild="1241262568014610482")
async def blackjack_game_command(ctx: discord.ApplicationContext):
    blackjack_game = blackjack.Game(2, decks=1)
    discord_player = blackjack.DiscordPlayer()
    blackjack_game.deal_cards()
    view = blackjack.BlackjackView(player_object=discord_player, game_object=blackjack_game)
    ctx = await ctx.respond("Starting a game of blackjack!", view=view)
    await view.start_game(ctx)


@bot.slash_command(name="roll",
                   description="roll a die",
                   test_guild="1241262568014610482")
async def roll_die(ctx: discord.ApplicationContext, sides: int = 6):
    if sides < 1:
        await ctx.respond("Die must have at least 1 side!")
        return
    await ctx.respond(f"Rolled a {random.randint(1, sides)}", view=DiceView(sides))


@bot.listen()
async def on_message(message):

    if message.author == bot.user:
        return

    print(f"Message sent in channel {message.channel}")
    if message.content[0] == "!":
        print(f"Command detected: {message.content}")
        await responses.handle_response(message, bot)


def run_bot():
    token = str(os.getenv("DISCORD_TOKEN"))
    bot.run(token)
