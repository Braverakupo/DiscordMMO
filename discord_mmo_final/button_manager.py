from typing import Dict, Any, List
from discord import ButtonStyle, ui, Interaction, Embed, File
import os
from state import load_player, save_player
from scene_loader import load_scene

# --------------------------------------------------------------------
# Apply effects: safe handling for numbers, lists, and strings
# --------------------------------------------------------------------
def _apply_effects(player: Dict[str, Any], effects: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply changes from button effects to the player state.
    - Numbers (hp/xp/gold/mana): increment
    - Lists (inventory): extend
    - Strings/other values: set directly
    """
    for key, change in effects.items():
        if isinstance(change, list):
            if key not in player or not isinstance(player[key], list):
                player[key] = []
            player[key].extend(change)

        elif isinstance(change, (int, float)):
            player[key] = player.get(key, 0) + change

        else:
            # e.g. active_training = "seal_stillness"
            player[key] = change
    return player

# --------------------------------------------------------------------
# Scene rendering to embeds
# --------------------------------------------------------------------
def scene_to_embed(scene: Dict[str, Any], player: Dict[str, Any], *, title_prefix: str = "") -> Embed:
    title = f"{title_prefix}{scene.get('title','Untitled')}"
    body = scene.get("body", "")
    e = Embed(title=title, description=body)

    if scene.get("image"):
        image_file = scene["image"]
        e.set_image(url=f"attachment://{os.path.basename(image_file)}")

    e.set_footer(
        text=f"HP {player.get('hp',0)} | XP {player.get('xp',0)} | "
             f"Gold {player.get('gold',0)} | Mana {player.get('mana',0)}"
    )
    return e

# --------------------------------------------------------------------
# Scene View & Buttons
# --------------------------------------------------------------------
class SceneView(ui.View):
    def __init__(self, owner_id: int, scene: Dict[str, Any], *, timeout: float = 1800):
        super().__init__(timeout=timeout)
        self.owner_id = owner_id
        self.scene = scene
        self._build_buttons(scene.get("buttons", []))

    def _build_buttons(self, buttons: List[Dict[str, Any]]):
        for b in buttons:
            b_type = b.get("type", "scene")
            label  = b.get("label", "Button")
            style  = ButtonStyle.primary if b_type == "scene" else ButtonStyle.success
            self.add_item(SceneButton(b, style=style))

class SceneButton(ui.Button):
    def __init__(self, btn_json: Dict[str, Any], *, style: ButtonStyle):
        super().__init__(label=btn_json.get("label", "Button"), style=style)
        self.btn_json = btn_json

    async def callback(self, interaction: Interaction):
        view: SceneView = self.view  # type: ignore
        if interaction.user.id != view.owner_id:
            await interaction.response.send_message(
                "This isn't your session. Use **!start** to begin your own.",
                ephemeral=True
            )
            return

        # Load player
        player = load_player(interaction.user.id)

        # Check requirements (e.g., requires mana/gold/etc.)
        requires = self.btn_json.get("requires", {})
        for key, amount in requires.items():
            if player.get(key, 0) < amount:
                await interaction.response.send_message(
                    f"🚫 You need {amount} {key} to do this.",
                    ephemeral=True
                )
                return

        # Apply action effects
        if self.btn_json.get("type") == "action":
            effects = self.btn_json.get("effects", {})
            player = _apply_effects(player, effects)
            save_player(interaction.user.id, player)

            # Simple feedback for action
            effect_text = ", ".join([f"{k} {v:+}" for k, v in effects.items()])
            if effect_text:
                await interaction.response.send_message(
                    f"✅ {effect_text}",
                    ephemeral=True
                )

            # If no next scene, stop here
            if not self.btn_json.get("next_scene"):
                return

            # Special case: training
            if "active_training" in effects:
                seal = effects["active_training"].replace("seal_", "").title()
                await interaction.followup.send(
                    f"🧘 You begin training **{seal}**.\n"
                    f"You will train for up to **24 hours**, "
                    f"consuming **10 mana every 10 minutes**.\n"
                    f"Remember to check in daily for your mastery bonus!",
                    ephemeral=True
                )

        # Move to next scene
        next_scene_name = self.btn_json.get("next_scene")
        if not next_scene_name:
            await interaction.response.send_message("🚫 No next scene defined.", ephemeral=True)
            return

        next_scene = load_scene(next_scene_name)
        new_view = SceneView(owner_id=view.owner_id, scene=next_scene)

        file = None
        if next_scene.get("image") and os.path.exists(next_scene["image"]):
            filename = os.path.basename(next_scene["image"])
            file = File(next_scene["image"], filename=filename)

        # Always reset attachments (so old ones don’t “stick”)
        await interaction.response.edit_message(
            embed=scene_to_embed(next_scene, player),
            view=new_view,
            attachments=[file] if file else []
        )
