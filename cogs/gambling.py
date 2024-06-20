import discord
from discord.ext import commands
from discord.ext import bridge
from database import db_commands as database
from game_logic import blackjack


# TODO: move the gambling commands to a separate cog (blackjack)
#       add more gambling commands like slots, roulette, etc.
#       add an economy leaderboard (this would probably be in the banking cog)


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name="blackjack",
                           aliases=["bj"],
                           description="play a game of blackjack",
                           test_guild="1241262568014610482")
    async def blackjack_game_command(self, ctx: discord.ApplicationContext, bet_amount: discord.Option(int) = 200):
        """
        Starts a game of blackjack and responds with the game state and appropriate buttons.
        :param ctx:
        :param bet_amount:
        :return:
        """
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
        view = blackjack.BlackjackView(player_object=discord_player,
                                       game_object=blackjack_game,
                                       bet_amount=bet_amount)
        ctx = await ctx.respond("Starting a game of blackjack!", view=view)
        await view.start_game(ctx)


def setup(bot):
    bot.add_cog(Gambling(bot))
