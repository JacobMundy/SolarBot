import asyncio
import random
import time

import discord
import os
import json
import math

from discord.ui import Button, View
import console_colors

# BELOW IS THE CODE FOR THE INVENTORY VIEW
class InventoryView(View):
    def __init__(self, ctx, inventory):
        super().__init__()
        self.ctx = ctx
        self.inventory = inventory
        self.page = 0
        self.embed = discord.Embed(title="Inventory", color=discord.Color.blue())
        avatar_url = self.get_avatar_url()
        self.embed.set_author(name=ctx.author.display_name, icon_url=avatar_url)
        self.update_embed()

    def get_avatar_url(self) -> str:
        """
        Returns the avatar URL of the user.
        :return: str
        """
        ctx = self.ctx
        return ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url

    def get_page(self) -> list:
        """
        Returns the items on the current page.
        :return: list
        """
        return self.inventory[self.page*5:(self.page+1)*5]

    def update_embed(self):
        """
        Updates the embed with the current page of items.
        :return:
        """
        self.embed.clear_fields()
        total_pages = math.ceil(len(self.inventory) / 5)
        self.embed.set_footer(text=f"Page {self.page+1}/{total_pages}")
        page_items = self.get_page()
        for item in page_items:
            self.embed.add_field(name=item['name'], value=f"Weight: {item['weight']}, Value: {item['value']}", inline=False)

    @discord.ui.button(label='Prev', style=discord.ButtonStyle.blurple)
    async def previous_button(self, button: Button, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            self.update_embed()
            await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label='✖', style=discord.ButtonStyle.danger)
    async def close_button(self, button: Button, interaction: discord.Interaction):
        await interaction.response.edit_message(delete_after=0)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple)
    async def next_button(self, button: Button, interaction: discord.Interaction):
        if (self.page + 1) * 5 < len(self.inventory):
            self.page += 1
            self.update_embed()
            await interaction.response.edit_message(embed=self.embed)

# BELOW IS THE CODE FOR THE FISHING LOGIC

# Define the path to the file
file_path = "database/fishing_inventory.json"

# Check if the inventory file exists
# If it does, load the inventory
# If it doesn't, create the file and set the inventory to an empty dictionary
def load_inventory() -> dict:
    """
    Loads the fishing inventory from the file
    :return: dict
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as inventory_loader:
            fishing_inventory = json.load(inventory_loader)
    else:
        with open(file_path, 'w') as inventory_loader:
            fishing_inventory = {}
            json.dump(fishing_inventory, inventory_loader)

    inventory_loader.close()
    return fishing_inventory

class FishingView(discord.ui.View):
    def __init__(self, ctx: discord.ApplicationContext):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.fish_on_line = None
        self.player_inventories = load_inventory()

    async def on_timeout(self):
        try:
            await self.ctx.edit(view=None)
            self.stop()
        except discord.errors.NotFound:
            print(f"{console_colors.FontColors.WARNING}"
                  f"Message was deleted/could not be found before timeout"
                  f"{console_colors.FontColors.END}")

    async def start_game(self):
        """
        Starts the fishing game.
        :return:
        """
        embed = discord.Embed(title="Fishing",
                              description="You cast your line into the water...",
                              color=discord.Color.blue())

        await self.ctx.respond(embed=embed, view=self)
        # Setup Timer to catch fish
        wait_time = random.randint(1,5)
        countdown = asyncio.create_task(asyncio.sleep(wait_time))

        # Setup interaction watcher
        interaction_task = asyncio.create_task(self.ctx.bot.wait_for('interaction'))

        done, pending = await asyncio.wait({countdown, interaction_task}, return_when=asyncio.FIRST_COMPLETED)

        if countdown in done:
            fish_rarity = random.choices(["common", "uncommon", "rare", "legendary"],
                                         weights=[0.3, 0.6, 0.08, 0.02],
                                         k=1)[0]
            with open(f"game_logic/fishing_data/{fish_rarity}.json", 'r') as random_fish:
                fish_data = json.load(random_fish)
                keys = list(fish_data.keys())
                selected_fish = random.choice(keys)

                # Get the fish data
                modified_fish = fish_data[selected_fish]

                # Modify the fish data for some fun and randomness
                length_modifier = random.uniform(0.5, 1.5)
                weight_modifier = random.uniform(0.5, 1.5) * length_modifier

                modified_fish["length"] = round(modified_fish["length"] * length_modifier, 2)
                modified_fish["weight"] = round(modified_fish["weight"] * weight_modifier, 2)
                modified_fish["value"] = round(modified_fish["value"] * weight_modifier, 0)

                self.fish_on_line = modified_fish
                random_fish.close()

            weight = self.fish_on_line["weight"]
            tug_message = "You feel a tug on the line..."
            time_to_reel = random.randint(1, 5)
            match weight:
                case weight if weight < 1:
                    tug_message = "You feel a light tug on the line..."
                    time_to_reel = random.randint(20, 30)
                case weight if weight > 5:
                    tug_message = "You feel a heavy tug on the line..."
                    time_to_reel = random.randint(10, 20)
                case weight if weight > 10:
                    tug_message = "You struggle against this fish!"
                    time_to_reel = random.randint(5, 10)
                case weight if weight > 20:
                    tug_message = "You are nearly pulled into the water!"
                    time_to_reel = 5

            time_since_epoch = int(time.time())

            embed = discord.Embed(title="Fishing",
                                  description=tug_message,
                                  color=discord.Color.blue())
            embed.add_field(name="Time to Reel", value=f"<t:{time_since_epoch + time_to_reel}:R>")
            await self.ctx.edit(embed=embed, view=self)
            interaction_task.cancel()

            countdown = asyncio.create_task(asyncio.sleep(time_to_reel))
            interaction_task = asyncio.create_task(self.ctx.bot.wait_for('interaction'))

            done, pending = await asyncio.wait({countdown, interaction_task},
                                               return_when=asyncio.FIRST_COMPLETED)

            if countdown in done:
                embed = discord.Embed(title="Fishing",
                                      description="The fish got away!",
                                      color=discord.Color.red())
                await self.ctx.edit(embed=embed, view=None)


    @discord.ui.button(label="Reel in", style=discord.ButtonStyle.primary)
    async def reel_in_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        'Reels' in the fish if it exists and displays the fish data.
        If the fish doesn't exist, displays a failure message.
        :param button:
        :param interaction:
        :return:
        """
        if self.fish_on_line is not None:
            if self.fish_on_line["name"][0].lower() in 'aeiou':
                article = "an"
            else:
                article = "a"

            embed = discord.Embed(title="Fishing",
                                  description=f"You reel in {article} {self.fish_on_line["name"]}!",
                                  color=discord.Color.green())
            embed.add_field(name="Length", value=f"{self.fish_on_line['length']} inches")
            embed.add_field(name="Weight", value=f"{self.fish_on_line['weight']} lbs")
            embed.add_field(name="Value", value=f"${self.fish_on_line['value']}")
            embed.set_image(url=self.fish_on_line["link"])
            await self.ctx.edit(embed=embed, view=None)

            fisherman_id = str(self.ctx.author.id)
            if fisherman_id in self.player_inventories:
                self.player_inventories[fisherman_id].append(self.fish_on_line)
            else:
                self.player_inventories[fisherman_id] = [self.fish_on_line]

            with open(file_path, 'w+') as inventory:
                json.dump(self.player_inventories, inventory)

        else:
            embed = discord.Embed(title="Fishing",
                                  description="You reeled too early!",
                                  color=discord.Color.red())
            await self.ctx.edit(embed=embed, view=None)