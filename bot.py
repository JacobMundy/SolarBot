import discord
import os

from discord.ui import Item

import blackjack

bot = discord.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


class MyView(discord.ui.View):
    @discord.ui.button(label="Click me!", row=0, style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("You clicked the button!")

    @discord.ui.button(label="no click me", row=0, style=discord.ButtonStyle.danger)
    async def button_callback2(self, button, interaction):
        await interaction.response.send_message("I will call a function next time.")

    @discord.ui.button(label="click me Ill actually call a function", row=1, style=discord.ButtonStyle.green)
    async def button_callback3(self, button, interaction):
        game_object = blackjack.Game()
        await interaction.response.send_message(str(game_object.get_deck()))

class BlackjackView(discord.ui.View):
    def __init__(self, player_object, game_object, *items: Item):
        super().__init__(*items)
        self.player_object = player_object
        self.game_object = game_object

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit_callback(self, button, interaction):
        self.player_object.set_move("hit", self.game_object)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.green)
    async def stand_callback(self, button, interaction):
        self.player_object.set_move("stand", self.game_object)

    @discord.ui.button(label="Double", style=discord.ButtonStyle.danger)
    async def double_callback(self, button, interaction):
        self.player_object.set_move("hit", self.game_object)


@bot.slash_command(name="hello",
                   description="Test a slash command.",
                   test_guild="1241262568014610482")
async def hello_command(ctx: discord.ApplicationContext):
    await ctx.respond("Hello World!", view=MyView())


@bot.slash_command(name="blackjack_test",
                   description="test the various blackjack functions",
                   test_guild="1241262568014610482")
async def blackjack_game_command(ctx: discord.ApplicationContext):
    blackjack_game = blackjack.Game(2, decks=1)
    discord_player = blackjack.DiscordPlayer()
    players = [blackjack.DealerBot(), discord_player]
    blackjack_game.deal_cards()
    player_moves = 0
    while blackjack_game.winner is None:
        view = BlackjackView(discord_player, blackjack_game)
        await ctx.respond(blackjack_game.get_board(), view=view)
        await view.wait()

    await ctx.respond(blackjack_game.get_board() + "\n Winner is Player" + blackjack_game.winner)






@bot.listen()
async def on_message(message):
    print(f"Message sent in channel {message.channel}")


def run_bot():
    token = str(os.getenv("DISCORD_TOKEN"))
    bot.run(token)
