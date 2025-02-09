# main.py
from pywaifu.godot import GodotConnector
from pywaifu.character import Character
#from pywaifu.vrm import VRMCharacter

def main():
    connector = GodotConnector("path/to/your/godot_project") #Replace
    connector.connect()

    yui = Character(
        name="Yui",
        personality="Kind, helpful, and a little clumsy.",
        godot_connector=connector
    )
    #OR, for VRM
    #yui = VRMCharacter(name="Yui", personality="Kind and helpful.", godot_connector=connector, vrm_node_path="/root/Scene/Yui")

    # Keep the script running (if not using godot-rl)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        connector.disconnect()

if __name__ == "__main__":
    main()