import json

import discord
from discord.ext import commands
from discord.ext import bridge

from game_logic import fishing
from database import db_commands as database


class Fishing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Setup choices for slash version of the commands
        # (their options are set in the setup function)
        self.item_choices = []

        fishing_inventory = "database/fishing_inventory.json"
        with open(fishing_inventory, 'r') as inventory_loader:
            whole_inventory = json.load(inventory_loader)
        inventory_loader.close()

        for user_id, player_inventory in whole_inventory.items():
            if player_inventory:
                item_in_inventory = [discord.OptionChoice(name=f"Name: {item["name"]} "
                                                          f"Weight: {item['weight']}, "
                                                          f"Value: {item['value']}",
                                                     value=item['name'].lower()) for item in player_inventory]
                self.item_choices.extend(item_in_inventory)

    @bridge.bridge_command(name="fish",
                           aliases=["cast"],
                           description="Go fishing",
                           test_guild="1241262568014610482")
    async def fish(self, ctx: discord.ApplicationContext):
        """
        Starts a game of fishing.
        :param ctx:
        :return:
        """
        view = fishing.FishingView(ctx)
        await view.start_game()

    @bridge.bridge_command(name="inventory",
                           description="Check your inventory",
                           test_guild="1241262568014610482")
    async def inventory(self, ctx: discord.ApplicationContext):
        """
        Responds with all the fish in a users inventory.
        :param ctx:
        :return:
        """
        user_id = str(ctx.author.id)
        fishing_inventory = "database/fishing_inventory.json"
        with open(fishing_inventory, 'r') as inventory_loader:
            inventory = json.load(inventory_loader).get(user_id, None)
        inventory_loader.close()


        if not inventory:
            await ctx.respond("You don't have any items in your inventory!")
        else:
            view = fishing.InventoryView(ctx, inventory)
            await ctx.respond(embed=view.embed, view=view)

    @bridge.bridge_command(name="sell",
                           description="Sell an item from your inventory",
                           test_guild="1241262568014610482")
    async def sell_item(self, ctx: discord.ApplicationContext, *, item: str):
        """
        Sells a specific item from the user's inventory.
        :param ctx:
        :param item:
        :return:
        """
        user_id = str(ctx.author.id)
        fishing_inventory = "database/fishing_inventory.json"
        with open(fishing_inventory, 'r') as inventory_loader:
            whole_inventory = json.load(inventory_loader)
            player_inventory = whole_inventory.get(user_id, None)
        inventory_loader.close()


        if not player_inventory:
            await ctx.respond("You don't have any items in your inventory!")
            return

        if not any(item_info['name'].lower() == item.lower() for item_info in player_inventory):
            await ctx.respond("You don't have that item in your inventory!")
            return

        matching_items = [item_info for item_info in player_inventory if item_info['name'].lower() == item.lower()]

        if len(matching_items) == 1:
            item_info = matching_items[0]
            item_value = item_info['value']
            player_inventory.remove(item_info)
            database.add_balance(user_id, item_value)
        else:
            embed = discord.Embed(title="Matching Items", color=discord.Color.blurple())
            for i, item_info in enumerate(matching_items):
                embed.add_field(name=item_info['name'],
                                value=f"Weight: {item_info['weight']}, Value: {item_info['value']}",
                                inline=False)
            response = await ctx.respond(embed=embed)

            # Add reactions to the message - limited to 10 items
            for i in range(min(10, len(matching_items))):
                await response.add_reaction(f'{i}\N{combining enclosing keycap}')

            def check(reaction_event, user_responded):
                return (user_responded == ctx.author
                        and str(reaction_event.emoji) in [f'{i}\N{combining enclosing keycap}' for i in range(10)])

            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            index = int(str(reaction.emoji)[0])  # Get the index from the reaction

            # Sell the item
            item_info = matching_items[index]
            item_value = item_info['value']
            player_inventory.remove(item_info)
            database.add_balance(user_id, item_value)

        # Save the changes to the *whole* inventory
        whole_inventory[user_id] = player_inventory

        # Save the changes to the file and respond
        with open(fishing_inventory, 'w') as inventory_saver:
            json.dump(whole_inventory, inventory_saver)
        inventory_saver.close()

        await ctx.respond(f"Sold {item} for {item_value}! \n"
                          f"Your balance is now: {database.get_balance(user_id)}")


    @bridge.bridge_command(name="sellall",
                           description="Sell all matching items from your inventory or sell all items",
                           test_guild="1241262568014610482")
    async def sell_all_items(self, ctx: discord.ApplicationContext, item: str = None):
        """
        Sells all matching items from the user's inventory
        or sells all items if left blank.
        :param ctx:
        :param item:
        :return:
        """
        user_id = str(ctx.author.id)
        fishing_inventory = "database/fishing_inventory.json"
        with open(fishing_inventory, 'r') as inventory_loader:
            whole_inventory = json.load(inventory_loader)
            player_inventory = whole_inventory.get(user_id, None)
        inventory_loader.close()

        if not player_inventory:
            await ctx.respond("You don't have any items in your inventory!")
            return

        if (item is not None) and (not any(item_info['name'].lower() == item.lower() for item_info in player_inventory)):
            await ctx.respond("You don't have that item in your inventory!")
            return


        if item is None:
            response = await ctx.respond("Are you sure you want to sell ALL your items?")
        else:
            response = await ctx.respond(f"Are you sure you want to sell all {item}s?")
        await response.add_reaction("✅")
        await response.add_reaction("❌")

        def check(reaction_event, user_responded):
            return user_responded == ctx.author and str(reaction_event.emoji) in ["✅", "❌"]

        reaction, user = await self.bot.wait_for('reaction_add', check=check)

        if str(reaction.emoji) == "❌":
            await ctx.respond("Cancelled!")
            return
        else:
            if item is None:
                total_value = sum(item_info['value'] for item_info in player_inventory)
                database.add_balance(user_id, total_value)
                whole_inventory[user_id] = []
            else:
                matching_items = [item_info for item_info in player_inventory if item_info['name'].lower() == item.lower()]
                total_value = sum(item_info['value'] for item_info in matching_items)
                player_inventory = [item_info for item_info in player_inventory if item_info['name'].lower() != item.lower()]
                database.add_balance(user_id, total_value)
                whole_inventory[user_id] = player_inventory

            with open(fishing_inventory, 'w') as inventory_saver:
                json.dump(whole_inventory, inventory_saver)
            inventory_saver.close()

            await ctx.respond(f"Sold all {item}s for {total_value}! \n"
                              f"Your balance is now: {database.get_balance(user_id)}")

def setup(bot):
    fishing_cog = Fishing(bot)
    bot.add_cog(Fishing(bot))

    limited_items = fishing_cog.item_choices[:25]
    limited_types = set(option.value for option in limited_items)

    fishing_cog.sell_all_items.options = [
        discord.Option(
            name="item",
            description="The type of fish you want to sell all of (leave blank to sell all items)",
            type=str,
            choices= limited_types,
            required=False
        )
    ]

    fishing_cog.sell_item.options = [
        discord.Option(
            name="item",
            description="The item you want to sell",
            type=str,
            choices=limited_items,
            required=True
        )
    ]