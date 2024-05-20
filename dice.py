import random
import discord


class DiceView(discord.ui.View):
    def __init__(self, sides: int):
        super().__init__()
        self.sides = sides

    @discord.ui.button(label="Re-roll", style=discord.ButtonStyle.primary)
    async def roll_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.message.edit(content=f"Rolled a {random.randint(1, self.sides)}", view=self)
