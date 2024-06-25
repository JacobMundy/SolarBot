import discord
from discord.ext import bridge
from discord.ext import commands
from database import db_commands as database


class Banking(commands.Cog):
    """
    The cog that holds the commands that modify or check the user's balance.
    """
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name="balance",
                           aliases=["bal"],
                           description="check your balance",
                           test_guild="1241262568014610482")
    async def check_balance(self, ctx: discord.ApplicationContext, user: discord.User = None):
        """
        Responds with balance of provided User.
        If no user is provided, responds with the balance of the author.
        :param ctx:
        :param user:
        :return:
        """
        if user is None:
            user_id = str(ctx.author.id)
            database.create_user(user_id)
            await ctx.respond(f"{ctx.author.name}'s balance: {database.get_balance(user_id)}")
        else:
            user_id = str(user.id)
            database.create_user(user_id)
            await ctx.respond(f"{user.name}'s balance: {database.get_balance(user_id)}")

    @bridge.bridge_command(name="daily",
                           description="claim your daily reward",
                           test_guild="1241262568014610482")
    async def daily_reward(self, ctx: discord.ApplicationContext):
        """
        Responds with the user's daily reward and balance.
        :param ctx:
        :return:
        """
        database.create_user(str(ctx.author.id))
        if database.claim_daily(str(ctx.author.id)):
            await ctx.respond("You have claimed your daily reward of 1000! \n"
                              "Your balance is now: " + str(database.get_balance(str(ctx.author.id))) + "\n")
        else:
            await ctx.respond(f"You have already claimed your daily reward! \n"
                              f"Try again in {database.get_time_until_next_daily(str(ctx.author.id))} hour(s).")

    @bridge.bridge_command(name="transfer",
                           description="transfer money to another user",
                           test_guild="1241262568014610482")
    async def transfer(self, ctx: discord.ApplicationContext, amount: int, user: discord.User):
        """
        Transfers money from the user to another user.
        :param ctx:
        :param amount:
        :param user:
        :return:
        """
        author_id = str(ctx.author.id)
        transferee = str(user.id)

        database.create_user(author_id)
        database.create_user(transferee)
        succeeded = database.transfer_money(author_id, transferee, amount)

        if succeeded:
            await ctx.respond(f"Transferred {amount} to {user.name}! \n"
                              f"Your balance is now: {database.get_balance(author_id)}")
        else:
            await ctx.respond("You don't have enough money to transfer that amount!")

    # TODO: turn this into a page based embed
    #       make it return user names instead of ids
    @bridge.bridge_command(name="leaderboard",
                           description="check the economy leaderboard",
                           test_guild="1241262568014610482")
    async def leaderboard(self, ctx: discord.ApplicationContext):
        """
        Responds with the top 10 users with the highest balance.
        :param ctx:
        :return:
        """
        leaderboard = database.get_leaderboard()
        response = "```Leaderboard:\n"
        for i, user in enumerate(leaderboard):
            response += f"{i + 1}. {user[0]}: {user[1]}\n"
        response += "```"
        await ctx.respond(response)


def setup(bot):
    bot.add_cog(Banking(bot))
