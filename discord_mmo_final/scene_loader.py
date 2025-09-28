import json

def load_scene(scene_name: str) -> dict:
    with open("scenes/world.json", "r", encoding="utf-8") as f:
        world = json.load(f)
    return world.get(scene_name, {
        "title": "Scene Missing",
        "body": f"Scene `{scene_name}` not found.",
        "buttons": []
    })


    scene = world[scene_name]
    return {
        "id": scene_name,
        "title": scene.get("title", "Untitled"),
        "body": scene.get("body", ""),
        "image": scene.get("image"),
        "buttons": scene.get("buttons", [])
    }
