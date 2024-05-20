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
        self.previous_move = None
        self.ctx = None

    def format_content(self, game_over=False):
        if game_over:
            dealer_hand = str(self.game_object.players[0])
            if self.game_object.winner[0][0] == 0:
                winner_text = "# Dealer wins!"
            elif self.game_object.winner[0][0] == 1:
                winner_text = "# You win!"
            else:
                winner_text = "# Push!"
        else:
            dealer_hand = str(self.game_object.get_board()[0])
            winner_text = ""

        dealer_hand = dealer_hand.replace("[", "")
        dealer_hand = dealer_hand.replace("]", "")
        dealer_hand = dealer_hand.replace("'", "")

        player_hand = str(self.game_object.get_board()[1])
        player_hand = player_hand.replace("[", "")
        player_hand = player_hand.replace("]", "")
        player_hand = player_hand.replace("'", "")

        return (f">>> # Dealers Hand \n "
                f"# {dealer_hand} \n\n"
                f"# Your Hand \n "
                f"# {player_hand} \n\n"
                f"\n\n# Your Score: {self.game_object.calculate_score(self.game_object.players[1])} \n"
                f"{winner_text}")

    async def start_game(self, ctx):
        self.ctx = ctx  # Store the context
        while self.game_object.winner is None:
            text_content = self.format_content()
            await ctx.respond(text_content, view=self)
            await self.wait()  # Wait for the user to interact with the buttons

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit_callback(self, button, interaction):
        await self.handle_move("hit", interaction)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.green)
    async def stand_callback(self, button, interaction):
        await self.handle_move("stand", interaction)

    @discord.ui.button(label="Double", style=discord.ButtonStyle.danger)
    async def double_callback(self, button, interaction):
        await self.handle_move("double", interaction)

    async def handle_move(self, move, interaction):
        self.player_object.set_move(move, self.game_object)
        self.previous_move = move
        await interaction.response.defer()
        player_score = self.game_object.calculate_score(self.game_object.players[1])

        if player_score < 21 and move != "stand":
            text_content = self.format_content()
            await interaction.message.edit(content=text_content, view=self)
        else:
            # Game is over, show the winner
            text_content = self.format_content(True)
            await interaction.message.edit(
                content=text_content, view=None)
            self.stop()


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
    blackjack_game.deal_cards()
    view = BlackjackView(player_object=discord_player, game_object=blackjack_game)
    await view.start_game(ctx)


@bot.listen()
async def on_message(message):
    print(f"Message sent in channel {message.channel}")


def run_bot():
    token = str(os.getenv("DISCORD_TOKEN"))
    bot.run(token)
