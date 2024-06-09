import asyncio
import random
import discord
import os
import json
import math

from discord.ui import Button, View

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
        """
        if self.ctx.author.avatar:
            return str(self.ctx.author.avatar.url)
        else:
            return f"https://cdn.discordapp.com/embed/avatars/{0}.png"

    def get_page(self):
        return self.inventory[self.page*5:(self.page+1)*5]

    def update_embed(self):
        self.embed.clear_fields()
        total_pages = math.ceil(len(self.inventory) / 5)
        self.embed.set_footer(text=f"Page {self.page+1}/{total_pages}")
        page_items = self.get_page()
        for item in page_items:
            self.embed.add_field(name=item['name'], value=f"Weight: {item['weight']}, Value: {item['value']}", inline=False)

    @discord.ui.button(label='Previous', style=discord.ButtonStyle.secondary)
    async def previous_button(self, button: Button, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            self.update_embed()
            await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.secondary)
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

    async def on_timeout(self) -> None:
        try:
            await self.ctx.edit(view=None)
            self.stop()
        except discord.errors.NotFound:
            print(f"Message was deleted/could not be found before timeout")

    async def start_game(self):
        await self.ctx.respond("You cast your line into the water...", view=self)
        # Setup Timer to catch fish
        wait_time = random.randint(1,5)
        countdown = asyncio.create_task(asyncio.sleep(wait_time))

        # Setup interaction watcher
        interaction_task = asyncio.create_task(self.ctx.bot.wait_for('interaction'))

        done, pending = await asyncio.wait({countdown, interaction_task}, return_when=asyncio.FIRST_COMPLETED)

        if countdown in done:
            #TODO: Planned "uncommon_fish", "rare_fish", "legendary_fish"
            fish_rarity = random.choice(["common"])
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

            await self.ctx.edit(content=f"You feel a tug on the line... It seems like a {self.fish_on_line["name"]}!",
                                view=self)
            interaction_task.cancel()

        if interaction_task in done:
            countdown.cancel()
            await self.ctx.edit(content="You reeled in too early!", view=None)


    @discord.ui.button(label="Reel in", style=discord.ButtonStyle.primary)
    async def reel_in_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.fish_on_line is not None:
            await self.ctx.edit(content=f"You reeled in a {self.fish_on_line["name"]}!", view=None)

            fisherman_id = str(self.ctx.author.id)
            if fisherman_id in self.player_inventories:
                self.player_inventories[fisherman_id].append(self.fish_on_line)
            else:
                self.player_inventories[fisherman_id] = [self.fish_on_line]

            with open(file_path, 'w+') as inventory:
                json.dump(self.player_inventories, inventory)

        else:
            await self.ctx.edit(content="You didnt catch anything!", view=None)