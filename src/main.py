# main.py (in the project root)
from pywaifu.godot import GodotConnector
from pywaifu.character import Character
# from pywaifu.vrm import VRMCharacter  # Use if you're using VRMCharacter

def main():
    connector = GodotConnector("path/to/your/godot_project")  # Replace with the actual path
    connector.connect()

    yui = Character(
        name="Yui",
        personality="Kind, helpful, and a little clumsy.",
        godot_connector=connector
    )
    # OR, if using VRMCharacter:
    # yui = VRMCharacter(
    #     name="Yui",
    #     personality="Kind and helpful.",
    #     godot_connector=connector,
    #     vrm_node_path="/root/Scene/Yui"  # Adjust path as needed
    # )

    # Keep the script running (if not using godot-rl, which handles this)
    try:
        while True:
            pass  # Or use a more sophisticated event loop if needed
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        connector.disconnect()

if __name__ == "__main__":
    main()