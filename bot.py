import discord
import os

import discord

bot = discord.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


class MyView(discord.ui.View):
    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("You clicked the button!")


@bot.slash_command(name="hello", description="Test a slash command.", test_guild="1241262568014610482")
async def hello_command(ctx: discord.ApplicationContext):
    await ctx.respond("Hello World!", view=MyView())


@bot.listen()
async def on_message(message):
    print(f"Message sent in channel {message.channel}")


def run_bot():
    token = str(os.getenv("DISCORD_TOKEN"))
    bot.run(token)
