import asyncio
import random
from itertools import cycle

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

    # TODO: add a view like blackjack so the game can be restarted without a new command
    @bridge.bridge_command(name="slots",
                             description="play a game of slots",
                            test_guild="1241262568014610482")
    async def slots_game_command(self, ctx: discord.ApplicationContext):
        """
        Starts a game of slots and responds with the game state and appropriate buttons.
        :param ctx:
        :return:
        """

        database.create_user(str(ctx.author.id))

        bet_amount = 200

        if database.get_balance(str(ctx.author.id)) < bet_amount:
            await ctx.respond(f"You don't have enough money to play slots ({bet_amount})!  \n"
                              "current balance: " + str(database.get_balance(str(ctx.author.id))))
            return


        # Define the symbols
        symbols = ["🍎", "🍊", "🍋", "🍒", "🍇", "🍉", "🍓", "🍑", "🍈", "🍌", "🍐", "🍍"]

        # Create a single message for the slot machine
        slot_message = await ctx.respond("Starting slots!")

        # Create three separate cycles for each wheel of the slot machine
        wheels = [cycle(random.sample(symbols, len(symbols))) for _ in range(3)]

        # Create a list of lists to store the symbols of each wheel
        wheel_symbols = [[next(wheel) for _ in range(3)] for wheel in wheels]

        # 0 = all wheels spinning, 1 = first wheel stopped,
        # 2 = second wheel stopped, 3 = error (so don't do that)
        async def loop_for_wheels(number_of_wheels: int):
            for _ in range(random.randint(3, 5)):
                for i in range(number_of_wheels, 3):
                    wheel_symbols[i].pop(0)
                    wheel_symbols[i].append(next(wheels[i]))

                await asyncio.sleep(0.5)
                wheel_strings = (f"==========" + "\n" +
                                 wheel_symbols[0][2] + "  " + wheel_symbols[1][2] + "  " + wheel_symbols[2][2] + "\n" +
                                 wheel_symbols[0][1] + "  " + wheel_symbols[1][1] + "  " + wheel_symbols[2][1] + "\n" +
                                 wheel_symbols[0][0] + "  " + wheel_symbols[1][0] + "  " + wheel_symbols[2][0] + "\n" +
                                 "==========" + "\n\n" +
                                 "Slots are spinning...")
                await slot_message.edit(content=" ".join(wheel_strings))

        await loop_for_wheels(0)
        await loop_for_wheels(1)
        await loop_for_wheels(2)

        # Calculate the reward based on the final symbols
        final_symbols = [wheel[1] for wheel in wheel_symbols]
        reward = sum([symbols.index(symbol) * 10 for symbol in final_symbols])

        # If symbols are the same, multiply the reward (a set cant have two of the same elements)
        if final_symbols[0] == final_symbols[1] == final_symbols[2]:
            reward *= 50
        elif len(set(final_symbols)) < 3:
            reward *= 10

        # Update the player's balance and display the reward
        database.add_balance(str(ctx.author.id), reward)

        final_string = (f"==========" + "\n" +
                         wheel_symbols[0][2] + "  " + wheel_symbols[1][2] + "  " + wheel_symbols[2][2] + "\n" +
                         wheel_symbols[0][1] + "  " + wheel_symbols[1][1] + "  " + wheel_symbols[2][1] + "\n" +
                         wheel_symbols[0][0] + "  " + wheel_symbols[1][0] + "  " + wheel_symbols[2][0] + "\n" +
                         "==========" + "\n\n" +
                         f"Slots Over! You won {reward}!")

        await slot_message.edit(content=" ".join(final_string))


def setup(bot):
    bot.add_cog(Gambling(bot))
