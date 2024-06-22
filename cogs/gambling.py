import asyncio
import random

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

    @bridge.bridge_command(name="slots",
                             description="play a game of slots",
                            test_guild="1241262568014610482")
    async def slots_game_command(self, ctx: discord.ApplicationContext):
        """
        Starts a game of slots and responds with the game state and appropriate buttons.
        :param ctx:
        :param bet_amount:
        :return:
        """

        database.create_user(str(ctx.author.id))

        bet_amount = 100

        if database.get_balance(str(ctx.author.id)) < bet_amount:
            await ctx.respond("You don't have enough money to bet that amount! \n"
                              "current balance: " + str(database.get_balance(str(ctx.author.id))))
            return


        # Define the symbols
        symbols = ["🍎", "🍊", "🍋", "🍒", "🍇", "🍉", "🍓", "🍑", "🍈", "🍌", "🍐", "🍍"]
        values = {"🍎": 10, "🍊": 20, "🍋": 30, "🍒": 40, "🍇": 50, "🍉": 60, "🍓": 70, "🍑": 80, "🍈": 90, "🍌": 100, "🍐": 110, "🍍": 120}


        # Randomly select three symbols
        slot_result = random.choices(symbols, k=3)

        # Check if the selected symbols match any of the winning combinations
        reward = 0
        if len(set(slot_result)) == 1:
            reward = values[slot_result[0]] * 100
        elif len(set(slot_result)) == 2:
            reward = values[slot_result[0]] * 10
        elif len(set(slot_result)) == 3:
            reward = values[slot_result[0]] * 3

        # Display the slot machine result with changing symbols
        slot_message = await ctx.respond(" ".join(random.choices(symbols, k=3)))
        for _ in range(3):
            await asyncio.sleep(1)
            await slot_message.edit(content=" ".join(random.choices(symbols, k=3)))
        await asyncio.sleep(0.5)
        await slot_message.edit(content=" ".join(slot_result))

        # Update the player's balance and display the reward
        database.add_balance(str(ctx.author.id), reward)
        await ctx.edit(f"{" ".join(slot_result)}\n You won {reward}! Your new balance is {database.get_balance(str(ctx.author.id))}")









def setup(bot):
    bot.add_cog(Gambling(bot))
