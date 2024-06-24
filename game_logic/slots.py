import asyncio
import random
from itertools import cycle

import discord.ui
from database import db_commands as database

class SlotsView(discord.ui.View):
    def __init__(self, ctx, bet):
        super().__init__()
        self.ctx = ctx
        self.bet = bet
        self.slot_message = None
        self.spinning = False

    async def on_timeout(self):
        try:
            await self.ctx.edit(view=None)
            self.stop()
        except discord.errors.NotFound:
            print(f"Message was deleted/could not be found before timeout")


    @discord.ui.button(label='Spin', style=discord.ButtonStyle.blurple)
    async def spin_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.spinning:
            await interaction.respond("Slots are already spinning!", ephemeral=True)
            return

        await interaction.response.defer()
        await self.play_slots()

    @discord.ui.button(label='✖', style=discord.ButtonStyle.danger)
    async def close_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(delete_after=0)

    async def update_message(self, content):
        if self.slot_message is None:
            self.slot_message = await self.ctx.respond(content, view=self)
        else:
            await self.slot_message.edit(content=content)


    async def play_slots(self):
        """
        Starts a game of slots and responds with the game state and appropriate buttons.
        :return:
        """
        self.spinning = True

        ctx = self.ctx
        database.create_user(str(ctx.author.id))

        bet_amount = 200

        if database.get_balance(str(ctx.author.id)) < bet_amount:
            await ctx.respond(f"You don't have enough money to play slots ({bet_amount})!  \n"
                              "current balance: " + str(database.get_balance(str(ctx.author.id))))
            return

        # Define the symbols
        symbols = ["🍎", "🍊", "🍋", "🍒", "🍇", "🍉", "🍓", "🍑", "🍈", "🍌", "🍐", "🍍"]

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
                await self.update_message(content=" ".join(wheel_strings))

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

        await self.update_message(content=" ".join(final_string))
        self.spinning = False