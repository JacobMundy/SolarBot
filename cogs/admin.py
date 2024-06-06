import discord
from discord.ext import commands
from database import db_commands as database
from console_colors import FontColors


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
        if not ctx.author.guild_permissions.manage_messages:
            response = await ctx.respond("You don't have the permissions to do that!", ephemeral=True)
            await response.delete(delay=20)
            return
        if not ctx.guild.me.guild_permissions.manage_messages:
            response = await ctx.respond("I don't have the permissions to do that!")
            await response.delete(delay=20)
            print(f" {FontColors.WARNING} "
                  f"Admin command invoked without (bot) permissions. "
                  f"{FontColors.END}")
            await ctx.respond("I don't have the permissions to do that!")
            return

        if user_id != 0:
            def check(message):
                return message.author.id == user_id

            confirmation = await ctx.respond(f"You are about to delete {amount} messages by user {user_id}. \n"
                                             f"Proceed? (y/n)")

            try:
                response = await self.bot.wait_for("message", check=check, timeout=30)
                if response.content.lower() != "y":
                    await confirmation.delete()
                    return
                await ctx.channel.purge(limit=amount + 3, check=check)
            except TimeoutError:
                await confirmation.delete()
        else:
            confirmation = await ctx.respond(f"You are about to delete {amount} messages. \n"
                                             f"Proceed? (y/n)")

            try:
                response = await self.bot.wait_for("message", timeout=30)
                if response.content.lower() != "y":
                    await confirmation.delete()
                    return
                await ctx.channel.purge(limit=amount + 3)
            except TimeoutError:
                await confirmation.delete()

    @commands.command(name="echo",
                      description="Echo a message",
                      test_guild="1241262568014610482")
    async def echo(self, ctx, *, message: str):
        """
        Echo a message.
        :param ctx:
        :param message:
        :return:
        """
        if not ctx.author.guild_permissions.manage_messages:
            response = await ctx.respond("You don't have the permissions to do that!", ephemeral=True)
            await response.delete(delay=20)
            return
        await ctx.send(message)
        await ctx.message.delete()

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
            embed = discord.Embed(title="Message Deleted",
                                  description=f"Message in {message.channel} by {message.author} has been deleted",
                                  color=discord.Color.red())
            embed.add_field(name="Message Content", value=message.content)
            embed.set_footer(text=f"Message ID: {message.id} \n"
                                  f"Message Date: {message.created_at}")
            embed.set_thumbnail(url=message.author.avatar.url)
            await channel.send(embed=embed)

        except AttributeError:
            print(f"{FontColors.WARNING} "
                  f"Channel {preferred_channel} not found. "
                  f"{FontColors.END}")
        except discord.errors.Forbidden:
            print(f"{FontColors.WARNING} "
                  f"Bot does not have permissions to send messages in the channel {preferred_channel}. "
                  f"{FontColors.END}")

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
            response = await ctx.respond("You don't have the permissions to do that!", ephemeral=True)
            await response.delete(delay=20)
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
            response = await ctx.respond("You don't have the permissions to do that!", ephemeral=True)
            await response.delete(delay=20)
            return

        channel = discord.utils.get(ctx.guild.channels, name=channel_name)
        if channel is None:
            await ctx.respond(f"Channel {channel_name} not found.")
            return

        database.set_settings("log_deleted_messages_channel", channel_name)
        await ctx.respond(f"Logging of deleted messages set to {channel_name}.")

    @commands.command(name="kick",
                      description="Kick a user",
                      test_guild="1241262568014610482")
    async def kick_user(self, ctx, user: discord.User, *, reason: str = "No reason provided"):
        """
        Kick a user.
        :param ctx:
        :param user:
        :param reason:
        :return:
        """
        if not ctx.author.guild_permissions.kick_members:
            response = await ctx.respond("You don't have the permissions to do that!", ephemeral=True)
            await response.delete(delay=20)
            return
        # Check if the bot has the permissions to kick members,
        # so we don't send a message to the user if the bot can't kick them
        if not ctx.guild.me.guild_permissions.kick_members:
            response = await ctx.respond("I don't have the permissions to do that!")
            await response.delete(delay=20)
            return

        # If the bot doesn't share a server with the user it
        # won't be able to send a message to them
        try:
            await user.send(f"You have been kicked from {ctx.guild} for {reason}.")
            await ctx.guild.kick(user, reason=reason)
            await ctx.respond(f"{user} has been kicked for {reason}.")

        except Exception as e:
            print(f"{FontColors.FAIL} "
                  f"Error: {e} "
                  f"{FontColors.END}")


def setup(bot):
    bot.add_cog(Admin(bot))
