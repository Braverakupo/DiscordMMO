import discord
from discord.ext import commands
from discord import File
import json
import asyncio # Keep for running the dojo loop
from typing import Optional

# --- Import from separated modules ---
from button_manager import SceneView
from state import dojo_training_loop, load_player
from scene_loader import load_scene
from discord_utils import scene_to_embed, get_scene_file # NEW

# ------------------------------------------------------
# Bot Setup
# ------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    # Start the background training loop when the bot is ready
    bot.loop.create_task(dojo_training_loop())

@bot.command()
async def start(ctx, scene_name: Optional[str] = "town_square"):
    """Starts a new game session or loads a specific scene."""
    
    # 1. Load scene and player state
    scene = load_scene(scene_name)
    player = load_player(ctx.author.id) 
    
    # 2. Prepare the view and attachments
    view = SceneView(owner_id=ctx.author.id, scene=scene)
    file = get_scene_file(scene) # Use helper function

    # 3. Send the message
    await ctx.send(
        embed=scene_to_embed(scene, player), # Use helper function
        view=view,
        files=[file] if file else None
    )

# ------------------------------------------------------
# Entry
# ------------------------------------------------------
if __name__ == "__main__":
    try:
        # Assuming your token is in 'tokenz.json'
        with open("tokenz.json", "r") as f:
            config = json.load(f)
        TOKEN = config["TOKEN"]
    except Exception as e:
        print("ERROR: Could not load token from tokenz.json.")
        exit()

    bot.run(TOKEN)
