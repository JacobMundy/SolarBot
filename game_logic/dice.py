import random
import discord
from console_colors import FontColors


class DiceView(discord.ui.View):
    def __init__(self, sides: int, ctx: discord.ApplicationContext):
        super().__init__(timeout=30)
        self.sides = sides
        self.ctx = ctx

    async def on_timeout(self) -> None:
        try:
            await self.ctx.edit(view=None)
            self.stop()
        except discord.errors.NotFound:
            print(f"{FontColors.WARNING}"
                  f"Message was deleted/could not be found before timeout"
                  f"{FontColors.END}")

    async def roll(self, respond=True):
        if self.sides < 1:
            await self.ctx.respond("Die must have at least 1 side!")
            return
        if respond:
            await self.ctx.respond(content=f"Rolled a {random.randint(1, self.sides)}", view=self)
        else:
            await self.ctx.edit(content=f"Rolled a {random.randint(1, self.sides)}", view=self)

    @discord.ui.button(label="Re-roll", style=discord.ButtonStyle.primary)
    async def roll_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.roll(respond=False)
