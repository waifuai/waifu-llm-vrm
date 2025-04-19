# examples/basic_usage.py
import time
from pywaifu.godot import GodotConnector, GodotError
from pywaifu.character import Character, LLMError # Import LLMError from character module now
# from pywaifu.vrm import VRMCharacter # Uncomment if using VRM

# --- Configuration ---
# IMPORTANT: Replace with the actual path to your Godot project directory
GODOT_PROJECT_PATH = "path/to/your/godot_project"
CHARACTER_NAME = "Yui"
CHARACTER_PERSONALITY = "Kind, helpful, and intelligent. Enjoys talking about technology."
# VRM configuration (only needed if USE_VRM is True)
VRM_NODE_PATH = "/root/Scene/YourVRMNode" # IMPORTANT: Set this path in Godot scene if using VRM
USE_VRM = False # Set to True to use the VRMCharacter example

def main():
    connector = None # Initialize connector to None for finally block
    try:
        # --- Pre-check ---
        # Although Character loads the key, checking beforehand can provide clearer errors.
        # You could import and call load_gemini_api_key() here if desired.
        print("Ensure your Google Gemini API key is stored in ~/.api-gemini")

        print("Initializing Godot Connector...")
        # Assuming Godot is already running and listening, or godot-rl will launch it
        connector = GodotConnector(GODOT_PROJECT_PATH)
        connector.connect()
        print("Connector ready.")

        print(f"Creating character: {CHARACTER_NAME}...")
        if USE_VRM:
            # Import VRMCharacter if needed
            from pywaifu.vrm import VRMCharacter
            waifu = VRMCharacter(
                name=CHARACTER_NAME,
                personality=CHARACTER_PERSONALITY,
                # model_name is no longer used
                godot_connector=connector,
                vrm_node_path=VRM_NODE_PATH
            )
            print("VRM Character created.")
        else:
            waifu = Character(
                name=CHARACTER_NAME,
                personality=CHARACTER_PERSONALITY,
                # model_name is no longer used
                godot_connector=connector
            )
            print("Standard Character created.")

        print(f"\n--- Starting interaction with {waifu.name} ---")
        print("Type 'quit' or 'exit' to end the conversation.")

        # Simple interactive loop
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit"]:
                break

            print(f"{waifu.name}: ...thinking...")
            try:
                response = waifu.talk(user_input)
                print(f"{waifu.name}: {response}")

                # Example VRM action (only if USE_VRM is True)
                if USE_VRM and isinstance(waifu, VRMCharacter):
                    # Add VRM-specific actions based on response or state
                    if "wave" in user_input.lower():
                         print(f"[{waifu.name} waves]")
                         waifu.play_animation("Wave") # Assuming 'Wave' animation exists
                         waifu.set_expression("Happy", 0.8) # Assuming 'Happy' blendshape exists
                    else:
                         # Default idle animation/expression
                         waifu.play_animation("Idle")
                         waifu.set_expression("Neutral", 1.0)

            except LLMError as e:
                print(f"LLM Error: {e}")
                # Decide if the loop should continue or break on LLM errors
                # break
            except GodotError as e:
                print(f"Godot Connection Error: {e}")
                print("Exiting due to connection error.")
                break
            except Exception as e:
                 print(f"An unexpected error occurred during talk: {e}")
                 # Optionally break the loop on unexpected errors
                 # break

    except GodotError as e:
        print(f"Failed to connect to Godot: {e}")
    except LLMError as e:
        # This catches errors during Character initialization (e.g., API key missing)
        print(f"Failed to initialize Character/LLM: {e}")
    except KeyboardInterrupt:
        print("\nUser interrupted. Exiting...")
    except Exception as e:
        # Catch-all for other unexpected errors during setup
        print(f"\nAn unexpected error occurred during setup: {e}")
    finally:
        if connector:
            print("Disconnecting from Godot...")
            connector.disconnect()
        print("Cleanup complete. Goodbye!")

if __name__ == "__main__":
    main()