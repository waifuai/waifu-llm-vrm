# pywaifu

A Python library for creating AI waifus in Godot, powered by the Google Gemini API and optionally using VRM models.

## Features

*   **AI Conversation:** Uses the Google Generative AI API (specifically `gemini-2.5-pro`) for natural language generation. Requires a Google Gemini API key.
*   **Godot Integration:** Connects to a running Godot instance for communication (using `godot-rl` if available, otherwise sockets).
*   **Character Representation:** `Character` class manages personality, state, and interaction logic, including initializing the Gemini chat session.
*   **VRM Support (Optional):** `VRMCharacter` subclass adds methods for controlling VRM animations and expressions via Godot.
*   **Context Management:** Conversation history is automatically managed by the Google Gemini chat session.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/waifuai/waifu-llm-vrm
    cd waifu-llm-vrm
    ```

2.  **Create a virtual environment (recommended):**
    This project uses `uv` for environment management. Ensure `uv` is installed (`pip install uv` or `python -m pip install uv`).
    ```bash
    # Create the venv
    python -m uv venv .venv
    # Activate (Bash/Git Bash)
    source .venv/Scripts/activate
    # Or (CMD on Windows)
    # .venv\Scripts\activate.bat
    # Or (PowerShell on Windows)
    # .venv\Scripts\Activate.ps1
    ```
    *Note: You might need to install `uv` inside the venv as well if you encounter issues: `.venv/Scripts/python.exe -m pip install uv`*

3.  **Set up Google Gemini API Key:**
    This library requires a Google Gemini API key.
    *   Obtain an API key from Google AI Studio (or your Google Cloud project).
    *   Create a file named `.api-gemini` in your home directory (`~/.api-gemini`).
    *   Paste your API key into this file and save it. The file should contain only the key.

4.  **Install dependencies:**
    Make sure your virtual environment is activated.
    ```bash
    # Install requirements using uv
    python -m uv pip install -r requirements.txt
    ```

## Usage

The following example demonstrates basic usage. You can find this script in `examples/basic_usage.py`.

```python
# examples/basic_usage.py
import time
from pywaifu.godot import GodotConnector, GodotError
from pywaifu.character import Character, LLMError # Import LLMError from character module now
# from pywaifu.vrm import VRMCharacter # Uncomment if using VRM

# --- Configuration ---
# IMPORTANT: Replace with the actual path to your Godot project directory
GODOT_PROJECT_PATH = "path/to/your/godot_project"
CHARACTER_NAME = "Yui"
CHARACTER_PERSONALITY = "Kind, helpful, and a little clumsy. Enjoys talking about technology."
# VRM configuration (only needed if USE_VRM is True)
VRM_NODE_PATH = "/root/Scene/YourVRMNode" # IMPORTANT: Set this path in Godot scene if using VRM
USE_VRM = False # Set to True to use the VRMCharacter example

def main():
    connector = None # Initialize connector to None for finally block
    try:
        # --- Pre-check ---
        # The Character class loads the key, but ensure the file exists.
        print("Ensure your Google Gemini API key is stored in ~/.api-gemini")

        print("Initializing Godot Connector...")
        # Assuming Godot is already running and listening, or godot-rl will launch it
        connector = GodotConnector(GODOT_PROJECT_PATH)
        connector.connect()
        print("Connector ready.")

        print(f"Creating character: {CHARACTER_NAME}...")
        # The Character class now automatically uses the Gemini API key
        # loaded from ~/.api-gemini and the 'gemini-2.5-pro' model.
        if USE_VRM:
            # Import VRMCharacter if needed
            from pywaifu.vrm import VRMCharacter
            waifu = VRMCharacter(
                name=CHARACTER_NAME,
                personality=CHARACTER_PERSONALITY,
                godot_connector=connector,
                vrm_node_path=VRM_NODE_PATH
            )
            print("VRM Character created.")
        else:
            waifu = Character(
                name=CHARACTER_NAME,
                personality=CHARACTER_PERSONALITY,
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
                    if "wave" in user_input.lower():
                         print(f"[{waifu.name} waves]")
                         waifu.play_animation("Wave")
                         waifu.set_expression("Happy", 0.8)
                    else:
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
        print(f"Failed to initialize Character/LLM: {e}")
    except KeyboardInterrupt:
        print("\nUser interrupted. Exiting...")
    except Exception as e:
        print(f"\nAn unexpected error occurred during setup: {e}")
    finally:
        if connector:
            print("Disconnecting from Godot...")
            connector.disconnect()
        print("Cleanup complete. Goodbye!")

if __name__ == "__main__":
    main()
```

## Godot Setup (Placeholder)

*   Instructions on setting up the Godot project side (e.g., required nodes, scripts for communication, VRM addon setup) need to be added here.
*   Ensure the Godot project listens on the correct port (default 9000 if not using `godot-rl`).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT-0 License