from typing import Dict, Any
from discord import ButtonStyle, ui, Interaction
import os

# --- New Imports ---
from state import load_player, save_player
from scene_loader import load_scene
from game_logic import apply_effects # NEW
from discord_utils import scene_to_embed, get_scene_file # NEW

# --------------------------------------------------------------------
# Core View Classes
# --------------------------------------------------------------------

class SceneButton(ui.Button):
    def __init__(self, label: str, style: ButtonStyle, custom_id: str, btn_json: Dict[str, Any]):
        super().__init__(label=label, style=style, custom_id=custom_id)
        self.btn_json = btn_json

    async def callback(self, interaction: Interaction):
        user_id = interaction.user.id
        view: SceneView = self.view # Type hint for easier access to view properties
        
        # 1. Check if the interaction is from the message owner
        if user_id != view.owner_id:
            await interaction.response.send_message("🚫 This is not your game session!", ephemeral=True)
            return

        # 2. Load player state
        player = load_player(user_id)
        
        # 3. Check requirements (not implemented in original but added for completeness)
        requires = self.btn_json.get("requires", {})
        for stat, value in requires.items():
            if player.get(stat, 0) < value:
                await interaction.response.send_message(
                    f"🚫 You need {value} {stat.title()} to do this!", 
                    ephemeral=True
                )
                return

        # 4. Apply effects & Save player state
        effects = self.btn_json.get("effects", {})
        if effects:
            player = apply_effects(player, effects) # Call new game_logic function
            save_player(user_id, player)

            # Special case for training
            if "active_training" in effects:
                seal = effects["active_training"].replace("seal_", "").title()
                await interaction.followup.send(
                    f"🧘 You begin training **{seal}**...",
                    ephemeral=True
                )

        # 5. Load next scene
        next_scene_name = self.btn_json.get("next_scene")
        if not next_scene_name:
            # If no next scene, just update the stats on the existing message
            await interaction.response.edit_message(
                embed=scene_to_embed(view.scene, player),
                view=view 
            )
            return

        next_scene = load_scene(next_scene_name)
        new_view = SceneView(owner_id=view.owner_id, scene=next_scene)

        # 6. Render and edit message
        file = get_scene_file(next_scene) # Call new discord_utils function

        await interaction.response.edit_message(
            embed=scene_to_embed(next_scene, player), # Call new discord_utils function
            view=new_view,
            attachments=[file] if file else []
        )


class SceneView(ui.View):
    def __init__(self, owner_id: int, scene: Dict[str, Any]):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.scene = scene

        # Add buttons dynamically
        for idx, btn_data in enumerate(scene.get("buttons", [])):
            button = SceneButton(
                label=btn_data["label"],
                style=ButtonStyle.grey,
                custom_id=f"scene_btn_{idx}",
                btn_json=btn_data
            )
            self.add_item(button)
