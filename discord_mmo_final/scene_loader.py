import discord
from discord import File
from typing import Dict, Any
import os

def scene_to_embed(scene: Dict[str, Any], player: Dict[str, Any], *, title_prefix: str = "▶ ") -> discord.Embed:
    """Converts a scene dictionary and player state into a rich Discord Embed."""
    
    # 1. Create the main embed content
    embed = discord.Embed(
        title=f"{title_prefix}{scene.get('title','Untitled')}",
        description=scene.get("body", ""),
        color=discord.Color.from_rgb(30, 30, 30) # Dark, sleek color
    )
    
    # 2. Set the image URL if available
    if scene.get("image"):
        image_file = scene["image"]
        # Use attachment:// for images that are uploaded as files
        embed.set_image(url=f"attachment://{os.path.basename(image_file)}")

    # 3. Add player stats to the footer
    stats = [
        f"💛 HP: {player.get('hp', 0)}",
        f"✨ Mana: {player.get('mana', 0)}",
        f"💰 Gold: {player.get('gold', 0)}",
        f"⭐ XP: {player.get('xp', 0)}",
    ]
    
    # Add active training status if present
    if player.get('active_training'):
         # Format like "Training: Stillness"
        training_name = player['active_training'].replace('seal_', '').title()
        stats.append(f"🧘 Training: {training_name}")

    embed.set_footer(text=" | ".join(stats))

    return embed

def get_scene_file(scene: Dict[str, Any]) -> File | None:
    """Return a discord.File object if the scene has a valid image path, else None."""
    if scene.get("image") and os.path.exists(scene["image"]):
        # Base name is used for the attachment:// reference in the embed
        filename = os.path.basename(scene["image"])
        return File(scene["image"], filename=filename)
    return None
