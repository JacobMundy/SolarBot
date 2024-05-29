import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="purge",
                      aliases=["md"],
                      description="Mass delete messages in a channel",
                      test_guild="1241262568014610482")
    async def mass_delete(self, ctx, amount: int, user_id: int = 0):
        """
        Mass delete specified number of messages in a channel.
        :param ctx:
        :param amount:
        :param user_id:
        :return:
        """
        try:
            if not ctx.author.guild_permissions.manage_messages:
                await ctx.respond("You don't have the permissions to do that!", ephemeral=True)
                return

            if user_id != 0:
                def check(message):
                    return message.author.id == user_id

                await ctx.channel.purge(limit=amount, check=check)
            else:
                await ctx.channel.purge(limit=amount)

        except discord.errors.Forbidden:
            print("Admin command invoked without permissions.")
            await ctx.respond("I don't have the permissions to do that!")


def setup(bot):
    bot.add_cog(Admin(bot))
