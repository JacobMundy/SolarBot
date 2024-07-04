import discord
from discord.ext import bridge, commands
from discord.ui import View


# This is the view that will be used to display the
# left and right arrows for the embeds as well as the close button
class HelpView(View):
    def __init__(self, pages, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = pages
        self.current_page = 0

    @discord.ui.button(label='Previous', style=discord.ButtonStyle.primary)
    async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.pages[self.current_page])

    @discord.ui.button(label='✖', style=discord.ButtonStyle.danger)
    async def close_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(delete_after=0)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.primary)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.pages[self.current_page])


# This is the cog that will contain the slash commands
class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="help",
                            description="Get help with the bot",
                            test_guild="1241262568014610482")
    async def help_command(self, ctx):
        char_limit = 400
        pages = []
        current_page = ""
        bot = self.bot

        for cog in bot.cogs.values():
            cog_name = getattr(cog, "qualified_name", "No Category")
            cog_commands = [f"/{cmd.name} {', '.join([f'<{param.name}>' for param in cmd.options])}" for cmd in
                            cog.get_commands() if
                            isinstance(cmd, discord.ext.bridge.core.BridgeSlashCommand)]
            if cog_commands:
                cog_embed = f"**{cog_name} Commands**\n{'\n'.join(cog_commands)}\n\n"
                if len(current_page + cog_embed) > char_limit:
                    pages.append(current_page)
                    current_page = cog_embed
                else:
                    current_page += cog_embed

        if current_page:
            pages.append(current_page)

        embeds = [discord.Embed(description=page, color=discord.Color.blurple()) for page in pages]
        for i, embed in enumerate(embeds):
            embed.set_footer(text=f"Page {i + 1} of {len(embeds)}")  # Set the footer to show the current page number

        view = HelpView(embeds)
        await ctx.respond(embed=embeds[0], view=view)


# This class overrides the default help command
# and formats the help embeds to be more user-friendly
class MyHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        """
        Returns the command signature.
        If the command is a slash command or bridge command, return an empty string.
        :param command:
        :return:
        """
        # Bridge commands cause errors when trying to get the signature
        # They also cause doubled commands in the help embed if they are included
        if isinstance(command, discord.ext.bridge.core.BridgeCommand):
            return ""
        elif isinstance(command, discord.ext.bridge.core.BridgeSlashCommand):
            return ""
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        """
        Sends the help embed for all cogs.
        :param mapping:
        :return:
        """
        pages = []
        current_page = ""
        char_limit = 400  # The character limit for a "page" in the help embed

        for cog, command_list in mapping.items():
            filtered = await self.filter_commands(command_list, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures.__contains__(""):
                command_signatures = filter(lambda string: string != "", command_signatures)

            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                cog_commands = "\n".join(command_signatures)
                cog_embed = f"**{cog_name} Commands**\n{cog_commands}\n\n"

                if len(current_page + cog_embed) > char_limit:
                    pages.append(current_page)
                    current_page = cog_embed
                else:
                    current_page += cog_embed


        if current_page:
            pages.append(current_page)

        embeds = [discord.Embed(description=page, color=discord.Color.blurple()) for page in pages]
        for i, embed in enumerate(embeds):
            embed.set_footer(text=f"Page {i + 1} of {len(embeds)}")  # Set the footer to show the current page number

        view = HelpView(embeds)
        channel = self.get_destination()
        await channel.send(embed=embeds[0], view=view)

    async def send_cog_help(self, cog):
        """
        Sends the help embed for a specific cog.
        :param cog:
        :return:
        """
        embed = discord.Embed(title=f"{cog.qualified_name} Commands", color=discord.Color.blurple())
        for command in cog.get_commands():
            if (not isinstance(command, discord.ext.bridge.core.BridgeSlashCommand)
                    and not isinstance(command, discord.ext.bridge.core.BridgeCommand)):

                command_signature = self.get_command_signature(command)
                embed.add_field(name=command_signature, value=command.description, inline=False)

        await self.send_embed(embed)

    async def send_command_help(self, command):
        """
        Sends the help embed for a specific command.
        :param command:
        :return:
        """
        embed = discord.Embed(title="Command Help", color=discord.Color.blurple())
        if not isinstance(command, discord.ext.bridge.core.BridgeSlashCommand):
            command_signature = self.get_command_signature(command)
            embed.add_field(name=command_signature, value=command.description, inline=False)

        await self.send_embed(embed)

    async def send_embed(self, embed: discord.Embed):
        """
        Sends the embed to the destination and waits for a reaction to delete the message.
        :param embed:
        :return:
        """
        response = await self.get_destination().send(embed=embed)
        await response.add_reaction("❌")
        reaction, user = await self.context.bot.wait_for('reaction_add', check=lambda r, u: r.message == response
                                                                                            and u == self.context.author)
        if str(reaction) == "❌":
            await response.delete()

def setup(bot: bridge.Bot):
    bot.add_cog(SlashCommands(bot))
    bot.help_command = MyHelp()