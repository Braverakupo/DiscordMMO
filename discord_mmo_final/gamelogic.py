from typing import Dict, Any, List

def apply_effects(player: Dict[str, Any], effects: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply changes from button effects to the player state.
    - Numbers (hp/xp/gold/mana): increment
    - Lists (inventory): extend
    - Strings/other values: set directly (e.g., active_training)
    """
    for key, change in effects.items():
        if isinstance(change, list):
            # Handle list extensions (e.g., adding to inventory)
            if key not in player or not isinstance(player[key], list):
                player[key] = []
            player[key].extend(change)

        elif isinstance(change, (int, float)):
            # Handle numerical increments (e.g., gold, xp, mana)
            player[key] = player.get(key, 0) + change

        else:
            # Handle direct assignments (e.g., setting active_training)
            player[key] = change
    return player
