"""
Project root main script for pywaifu.

This script serves as the main entry point for the pywaifu library when run from the project root.
It demonstrates basic character creation and connection to Godot without VRM functionality.

The script provides:
- Basic character creation with personality
- Simple connection to Godot project
- Basic conversational interface
- Error handling and cleanup

Usage:
    1. Set up your Google Gemini API key in ~/.api-gemini
    2. Update the Godot project path to point to your actual Godot project directory
    3. Run: python src/main.py

Note: This is a simple example script. For more advanced features,
see the examples in the examples/ directory.
"""
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