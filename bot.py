import discord
import os

from dotenv import load_dotenv
from discord.ext import bridge
from console_colors import FontColors
from database import db_commands as database
from cogs.help import MyHelp

load_dotenv()

# Add any cogs you want to load here,
# should be names of the files in the cogs directory
cogs_list = ['banking',
             'games',
             'fun',
             'fishing_cog',
             'admin']

bot = bridge.Bot(command_prefix="!", intents=discord.Intents.all())
bot.help_command = MyHelp()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_command(ctx):
    if database.is_blacklisted_channel(str(ctx.channel.id)):
        return

    cog_name = ctx.command.cog_name if ctx.command.cog_name else "None"
    if cog_name == "Admin":
        print(f"{FontColors.OK_GREEN} "
              f"Admin Command requested: {ctx.command} \n"
              f"Called by: {ctx.author} "
              f"{FontColors.END}")
    else:
        print(f"{FontColors.OK_BLUE} "
              f"Command: {ctx.command} "
              f"{FontColors.END}")

# This will probably be moved to a cog in the future to handle more events
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        param_list = ctx.command.clean_params.keys()
        params = ", ".join(param_list)
        command = ctx.command.qualified_name
        embed = discord.Embed(title="Missing required argument!",
                              description=f"```{command}: {params}```",
                              color=discord.Color.red())
        await ctx.respond(embed=embed)

    elif isinstance(error, discord.ext.commands.errors.UserNotFound):
        embed = discord.Embed(title="User not found!",
                              description="The user you are trying to find does not exist.",
                              color=discord.Color.red())
        await ctx.respond(embed=embed)

    else:
        print(f"{FontColors.FAIL} "
              f"Error: {error} "
              f"{FontColors.END}")



@bot.check
async def blacklist_check(ctx):
    return (not database.is_blacklisted_channel(str(ctx.channel.id))
            or str(ctx.command) == "unblacklist_channel")


def run_bot():
    for cog in cogs_list:
        bot.load_extension(f"cogs.{cog}")
    token = str(os.getenv("DISCORD_TOKEN"))
    bot.run(token)
