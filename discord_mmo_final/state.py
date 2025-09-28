import json
import os
import asyncio
import time

PLAYERS_DIR = "players"

def _ensure_dirs():
    if not os.path.exists(PLAYERS_DIR):
        os.makedirs(PLAYERS_DIR)

def _player_path(user_id: int) -> str:
    _ensure_dirs()
    return os.path.join(PLAYERS_DIR, f"{user_id}.json")

def default_player() -> dict:
    return {
        "hp": 100,
        "xp": 0,
        "gold": 0,
        "inventory": [],
        "mana": 500,
        "active_training": None,      # e.g. "seal_flame"
        "training_start": None,       # timestamp when training began
        "seal_stillness": 0,
        "seal_flame": 0,
        "seal_flow": 0,
        "seal_stone": 0,
        "seal_gale": 0,
        "seal_echo": 0,
        "seal_shadow": 0,
        "seal_radiance": 0,
        "mastery": 0
    }

def load_player(user_id: int) -> dict:
    path = _player_path(user_id)
    if not os.path.exists(path):
        return default_player()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_player(user_id: int, data: dict) -> None:
    path = _player_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# -------------------------------------------------------------
# Background Dojo Training Loop
# -------------------------------------------------------------
async def dojo_training_loop():
    """Run every 10 minutes, update all players currently training."""
    while True:
        _ensure_dirs()
        for fname in os.listdir(PLAYERS_DIR):
            if not fname.endswith(".json"):
                continue

            path = os.path.join(PLAYERS_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                player = json.load(f)

            active = player.get("active_training")
            if active:
                # Ensure training_start is set
                if not player.get("training_start"):
                    player["training_start"] = int(time.time())

                # Stop after 24h (86400 seconds)
                elapsed = int(time.time()) - player["training_start"]
                if elapsed >= 86400:  # 24 hours
                    print(f"[DOJO] {fname} finished 24h training in {active}. Autostop.")
                    player["active_training"] = None
                    player["training_start"] = None
                elif player.get("mana", 0) >= 10:
                    # Consume mana and increment stat
                    if active not in player:
                        player[active] = 0
                    player[active] += 1
                    player["mana"] -= 10
                    print(f"[DOJO] {fname} trained {active} → {player[active]} (Mana left {player['mana']})")

            with open(path, "w", encoding="utf-8") as f:
                json.dump(player, f, indent=2)

        await asyncio.sleep(600)  # 10 minutes per tick
