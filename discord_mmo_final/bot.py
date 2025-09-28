import json
import discord
from discord.ext import commands
from discord import ui, ButtonStyle, File
import os

# ------------------------------------------------------
# Scene Loader
# ------------------------------------------------------
def load_scene(scene_name: str) -> dict:
    with open("world.json", "r", encoding="utf-8") as f:
        world = json.load(f)
    return world.get(scene_name, {
        "title": "Scene Missing",
        "body": f"Scene `{scene_name}` not found.",
        "buttons": []
    })

# ------------------------------------------------------
# Scene Renderer
# ------------------------------------------------------
def scene_to_embed(scene: dict, title_prefix: str = "▶ ") -> discord.Embed:
    embed = discord.Embed(
        title=f"{title_prefix}{scene.get('title','Untitled')}",
        description=scene.get("body", "")
    )
    if scene.get("image"):
        image_file = scene["image"]
        embed.set_image(url=f"attachment://{os.path.basename(image_file)}")
    return embed

# ------------------------------------------------------
# Helper: Get File for Scene Image
# ------------------------------------------------------
def _get_scene_file(scene: dict):
    """Return a discord.File if the scene has a valid image path, else None."""
    if scene.get("image") and os.path.exists(scene["image"]):
        filename = os.path.basename(scene["image"])
        return File(scene["image"], filename=filename)
    return None

# ------------------------------------------------------
# Scene View & Buttons
# ------------------------------------------------------
class SceneView(ui.View):
    def __init__(self, scene: dict, *, timeout: float = 1800):
        super().__init__(timeout=timeout)
        for b in scene.get("buttons", []):
            self.add_item(SceneButton(b))

class SceneButton(ui.Button):
    def __init__(self, btn_json: dict):
        super().__init__(label=btn_json.get("label", "Next"), style=ButtonStyle.primary)
        self.btn_json = btn_json

    async def callback(self, interaction: discord.Interaction):
        # --------------------------------------------------
        # Effects + Requires (dormant, no-op for now)
        # --------------------------------------------------
        requires = self.btn_json.get("requires", {})
        effects  = self.btn_json.get("effects", {})

        if requires or effects:
            print(f"DEBUG: Button '{self.label}' pressed. Requires={requires}, Effects={effects}")

        # --------------------------------------------------
        # Navigate to next scene
        # --------------------------------------------------
        next_scene_name = self.btn_json.get("next_scene")
        if not next_scene_name:
            await interaction.response.send_message("🚫 No next scene defined.", ephemeral=True)
            return

        next_scene = load_scene(next_scene_name)
        new_view = SceneView(next_scene)
        file = _get_scene_file(next_scene)

        await interaction.response.edit_message(
            embed=scene_to_embed(next_scene),
            view=new_view,
            attachments=[file] if file else []
        )

# ------------------------------------------------------
# Bot Setup
# ------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.command()
async def start(ctx, scene_name: str = "town_square"):
    scene = load_scene(scene_name)
    view = SceneView(scene)
    file = _get_scene_file(scene)

    await ctx.send(
        embed=scene_to_embed(scene),
        view=view,
        files=[file] if file else None
    )

# ------------------------------------------------------
# Entry
# ------------------------------------------------------
if __name__ == "__main__":
    with open("tokenz.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)
    TOKEN = cfg["TOKEN"]
    bot.run(TOKEN)
