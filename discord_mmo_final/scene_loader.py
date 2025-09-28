import json
import os

# Assuming world.json is in the root or a 'scenes' directory based on your snippets
WORLD_FILE = "world.json" # Change to "scenes/world.json" if it's in a subdirectory

def load_scene(scene_name: str) -> dict:
    """
    Retrieves all data for a single game scene from world.json.
    """
    try:
        with open(WORLD_FILE, "r", encoding="utf-8") as f:
            world = json.load(f)
        
        # Return the scene if it exists, otherwise return the error scene
        return world.get(scene_name, {
            "title": "Scene Missing",
            "body": f"Scene `{scene_name}` not found. Check your `world.json` file.",
            "buttons": []
        })

    except FileNotFoundError:
        print(f"ERROR: World file '{WORLD_FILE}' not found.")
        return {
            "title": "SYSTEM ERROR",
            "body": f"The game world file (`{WORLD_FILE}`) is missing or inaccessible.",
            "buttons": []
        }
    except json.JSONDecodeError:
        print(f"ERROR: World file '{WORLD_FILE}' is not valid JSON.")
        return {
            "title": "SYSTEM ERROR",
            "body": f"The game world file (`{WORLD_FILE}`) is corrupt.",
            "buttons": []
        }
