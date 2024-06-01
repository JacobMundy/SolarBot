import discord
from discord.ext import commands

import database


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

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Logs deleted messages.
        :param message:
        :return:
        """
        logs_enabled = database.get_settings("log_deleted_messages")
        preferred_channel = database.get_settings("log_deleted_messages_channel")
        channel = discord.utils.get(message.guild.channels, name=preferred_channel)
        if logs_enabled == 0 or message.channel == channel:
            print("Logging of deleted messages is disabled.")
            return

        try:
            await channel.send(f"Message deleted in {message.channel} by {message.author}: {message.content}")
        except discord.errors.Forbidden and AttributeError:
            if channel is None:
                print(f"\033[93m Channel {preferred_channel} not found. \033[0m")
            else:
                print("\033[93m Bot does not have permissions to send messages in the specified channel. \033[0m")

    @commands.command(name="toggle_logs",
                      description="Toggle logging of deleted messages",
                      test_guild="1241262568014610482")
    async def toggle_logs(self, ctx):
        """
        Toggles logging of deleted messages.
        :param ctx:
        :return:
        """
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.respond("You don't have the permissions to do that!", ephemeral=True)
            return

        if database.get_settings("log_deleted_messages") == 1:
            database.set_settings("log_deleted_messages", 0)
            await ctx.respond("Logging of deleted messages disabled.")
        else:
            database.set_settings("log_deleted_messages", 1)
            await ctx.respond("Logging of deleted messages enabled.")

    @commands.command(name="set_logs_channel",
                      description="Set the channel to log deleted messages",
                      test_guild="1241262568014610482")
    async def set_logs_channel(self, ctx, channel_name: str):
        """
        Set the channel to log deleted messages.
        :param ctx:
        :param channel_name:
        :return:
        """
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.respond("You don't have the permissions to do that!", ephemeral=True)
            return

        channel = discord.utils.get(ctx.guild.channels, name=channel_name)
        if channel is None:
            await ctx.respond(f"Channel {channel_name} not found.")
            return

        database.set_settings("log_deleted_messages_channel", channel_name)
        await ctx.respond(f"Logging of deleted messages set to {channel_name}.")


def setup(bot):
    bot.add_cog(Admin(bot))
