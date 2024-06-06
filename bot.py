import discord
import os
from discord.ext import bridge
from console_colors import FontColors

# Add any cogs you want to load here,
# should be names of the files in the cogs directory
cogs_list = ['banking',
             'games',
             'fun',
             'admin']

bot = bridge.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_command(ctx):
    cog_name = ctx.command.cog_name if ctx.command.cog_name else "None"
    if cog_name == "Admin":
        print(f"{FontColors.OK_GREEN} "
              f"Admin Command: {ctx.command} "
              f"{FontColors.END}")
    else:
        print(f"{FontColors.OK_BLUE} "
              f"Command: {ctx.command} "
              f"{FontColors.END}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        print(f"{FontColors.WARNING} "
              f"Missing required argument in command: {ctx.command}"
              f"{FontColors.END}")


def run_bot():
    for cog in cogs_list:
        bot.load_extension(f"cogs.{cog}")
    token = str(os.getenv("DISCORD_TOKEN"))
    bot.run(token)
