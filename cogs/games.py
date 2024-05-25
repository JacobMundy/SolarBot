import discord
from discord.ext import bridge
from discord.ext import commands
import database
import blackjack
from dice import DiceView


async def start_blackjack(ctx: discord.ApplicationContext, bet_amount: int):
    database.create_user(str(ctx.author.id))

    if bet_amount < 200:  # Minimum bet amount
        await ctx.respond("Minimum bet amount is 200!")
        return

    if database.get_balance(str(ctx.author.id)) < bet_amount:
        await ctx.respond("You don't have enough money to bet that amount! \n"
                          "current balance: " + str(database.get_balance(str(ctx.author.id))))
        return

    blackjack_game = blackjack.Game(2, decks=1)
    discord_player = blackjack.DiscordPlayer()
    blackjack_game.deal_cards()
    view = blackjack.BlackjackView(player_object=discord_player, game_object=blackjack_game, bet_amount=bet_amount)
    ctx = await ctx.respond("Starting a game of blackjack!", view=view)
    await view.start_game(ctx)


async def start_dice(ctx: discord.ApplicationContext, sides: int):
    view = DiceView(sides=sides, ctx=ctx)
    await view.roll()


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name="blackjack",
                           description="play a game of blackjack",
                           test_guild="1241262568014610482")
    async def blackjack_game_command(self, ctx: discord.ApplicationContext, bet_amount: discord.Option(int) = 200):
        await start_blackjack(ctx, bet_amount)

    @bridge.bridge_command(name="roll",
                           description="roll a die",
                           test_guild="1241262568014610482")
    async def roll_die(self, ctx: discord.ApplicationContext, sides: int = 6):
        await start_dice(ctx, sides)

    # FOLLOWING IS FOR ALIASES
    @commands.command(name="bj",
                      description="play a game of blackjack",
                      test_guild="1241262568014610482")
    async def blackjack_game_command_aliases(self, ctx: discord.ApplicationContext,
                                             bet_amount: int = 200):
        await start_blackjack(ctx, bet_amount)