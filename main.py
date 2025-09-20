"""
Example usage script for pywaifu.

This script demonstrates how to create an AI character with both standard and VRM functionality.
It shows basic character creation, conversation handling, and VRM animation control.

The script includes:
- Character creation with personality traits
- Interactive conversation loop
- VRM animation and expression control
- Error handling for both LLM and Godot connections
- Graceful cleanup on exit

Usage:
    1. Set up your Google Gemini API key in ~/.api-gemini
    2. Update GODOT_PROJECT_PATH to point to your Godot project directory
    3. Set USE_VRM to True if you want to use VRM features
    4. Run: python main.py

Configuration:
    - GODOT_PROJECT_PATH: Path to your Godot project directory
    - CHARACTER_NAME: Name of the AI character
    - CHARACTER_PERSONALITY: Personality description for the character
    - MODEL_NAME: Optional Hugging Face model name (set to None for default)
    - VRM_NODE_PATH: Node path for VRM model in Godot scene
    - USE_VRM: Set to True to enable VRM functionality
"""
import time
from pywaifu.godot import GodotConnector, GodotError
from pywaifu.character import Character
from pywaifu.vrm import VRMCharacter # Keep for VRM example option
from pywaifu.llm import LLMError

# --- Configuration ---
# IMPORTANT: Replace with the actual path to your Godot project directory
GODOT_PROJECT_PATH = "path/to/your/godot_project"
# Define character details
CHARACTER_NAME = "Aiko"
CHARACTER_PERSONALITY = "Energetic, optimistic, and loves discussing video games."
# Optional: Specify a different Hugging Face model (e.g., "gpt2")
# Set to None to use the default "distilgpt2"
MODEL_NAME = None
# Optional: Set path for VRM model if using VRMCharacter
VRM_NODE_PATH = "/root/Scene/YourVRMNode" # Adjust as needed in your Godot scene
USE_VRM = False # Set to True to use the VRMCharacter example

def main():
    connector = None # Initialize connector to None for finally block
    try:
        print("Initializing Godot Connector...")
        # Assuming Godot is already running and listening, or godot-rl will launch it
        connector = GodotConnector(GODOT_PROJECT_PATH)
        connector.connect()
        print("Connector ready.")

        print(f"Creating character: {CHARACTER_NAME}...")
        if USE_VRM:
            waifu = VRMCharacter(
                name=CHARACTER_NAME,
                personality=CHARACTER_PERSONALITY,
                model_name=MODEL_NAME,
                godot_connector=connector,
                vrm_node_path=VRM_NODE_PATH
            )
            print("VRM Character created.")
        else:
            waifu = Character(
                name=CHARACTER_NAME,
                personality=CHARACTER_PERSONALITY,
                model_name=MODEL_NAME,
                godot_connector=connector
            )
            print("Standard Character created.")

        print(f"\n--- Starting interaction with {waifu.name} ---")
        print("Type 'quit' or 'exit' to end the conversation.")

        while True:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit"]:
                break

            print(f"{waifu.name}: ...thinking...")
            try:
                response = waifu.talk(user_input)
                print(f"{waifu.name}: {response}")

                # Example VRM action based on response (simple keyword check)
                if USE_VRM and "game" in response.lower():
                     print(f"[{waifu.name} performs 'excited' animation]")
                     waifu.play_animation("Excited") # Assuming 'Excited' animation exists
                     waifu.set_expression("Joy", 0.7) # Assuming 'Joy' blendshape exists
                elif USE_VRM:
                     # Default idle animation/expression
                     waifu.play_animation("Idle")
                     waifu.set_expression("Neutral", 1.0)


            except LLMError as e:
                print(f"LLM Error: {e}")
            except GodotError as e:
                print(f"Godot Connection Error: {e}")
                print("Exiting due to connection error.")
                break
            except Exception as e:
                 print(f"An unexpected error occurred during talk: {e}")


    except GodotError as e:
        print(f"Failed to connect to Godot: {e}")
    except LLMError as e:
        print(f"Failed to initialize LLM: {e}")

    except KeyboardInterrupt:
        print("\nUser interrupted. Exiting...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if connector:
            print("Disconnecting from Godot...")
            connector.disconnect()
        print("Cleanup complete. Goodbye!")

if __name__ == "__main__":
    main()