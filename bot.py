import discord
import os
import blackjack

bot = discord.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.slash_command(name="blackjack_test",
                   description="test the various blackjack functions",
                   test_guild="1241262568014610482")
async def blackjack_game_command(ctx: discord.ApplicationContext):
    blackjack_game = blackjack.Game(2, decks=1)
    discord_player = blackjack.DiscordPlayer()
    blackjack_game.deal_cards()
    view = blackjack.BlackjackView(player_object=discord_player, game_object=blackjack_game)
    await view.start_game(ctx)


@bot.listen()
async def on_message(message):
    print(f"Message sent in channel {message.channel}")


def run_bot():
    token = str(os.getenv("DISCORD_TOKEN"))
    bot.run(token)
