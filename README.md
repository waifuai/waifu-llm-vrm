# pywaifu

A Python library for creating AI waifus in Godot, powered by Hugging Face Transformers and optionally using VRM models.

## Features

*   **AI Conversation:** Uses Hugging Face `transformers` library for natural language generation. Defaults to `distilgpt2` but configurable.
*   **Godot Integration:** Connects to a running Godot instance for communication (using `godot-rl` if available, otherwise sockets).
*   **Character Representation:** `Character` class manages personality, state, and interaction logic.
*   **VRM Support (Optional):** `VRMCharacter` subclass adds methods for controlling VRM animations and expressions via Godot.
*   **Context Management:** Basic conversation history tracking and truncation.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/waifuai/waifu-llm-vrm.git # Replace with actual URL
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

3.  **Install dependencies:**
    Make sure your virtual environment is activated. The requirements include `torch` with CUDA support if available.
    ```bash
    # Install requirements using uv
    python -m uv pip install -r requirements.txt
    # If torch CUDA install fails via requirements.txt, install separately:
    # python -m uv pip install torch --index-url https://download.pytorch.org/whl/cu121 # Adjust cuXXX for your CUDA version
    ```

## Usage

```python
from pywaifu.godot import GodotConnector
from pywaifu.character import Character
# from pywaifu.vrm import VRMCharacter # Uncomment if using VRM

# --- Configuration ---
GODOT_PROJECT_PATH = "path/to/your/godot_project" # IMPORTANT: Set this path
CHARACTER_NAME = "Yui"
CHARACTER_PERSONALITY = "Kind, helpful, and a little clumsy. Enjoys talking about technology."
# Optional: Specify a different Hugging Face model
# MODEL_NAME = "gpt2" # Example: Use standard GPT-2
MODEL_NAME = None # Use default (distilgpt2)

# --- Setup ---
# Ensure Godot project is running and listening for connections
# (See Godot setup instructions - TBD)
connector = GodotConnector(GODOT_PROJECT_PATH)
try:
    connector.connect() # Connects using godot-rl or sockets

    # --- Create Character ---
    # Basic Character
    waifu = Character(
        name=CHARACTER_NAME,
        personality=CHARACTER_PERSONALITY,
        model_name=MODEL_NAME, # Pass the model name here
        godot_connector=connector
    )

    # OR VRM Character (if using VRM)
    # VRM_NODE_PATH = "/root/Scene/YourVRMNode" # IMPORTANT: Set this path in Godot scene
    # waifu = VRMCharacter(
    #     name=CHARACTER_NAME,
    #     personality=CHARACTER_PERSONALITY,
    #     model_name=MODEL_NAME,
    #     godot_connector=connector,
    #     vrm_node_path=VRM_NODE_PATH
    # )

    print(f"{waifu.name} is ready!")

    # --- Interaction Example ---
    user_input = "Hello there!"
    print(f"\nYou: {user_input}")
    response = waifu.talk(user_input)
    print(f"{waifu.name}: {response}")

    user_input = "What are you thinking about?"
    print(f"\nYou: {user_input}")
    response = waifu.talk(user_input)
    print(f"{waifu.name}: {response}")

    # --- Optional: VRM Action Example ---
    # if isinstance(waifu, VRMCharacter):
    #     print("\nMaking Yui wave...")
    #     waifu.play_animation("Wave") # Assuming 'Wave' animation exists
    #     waifu.set_expression("Happy", 0.8) # Assuming 'Happy' blendshape exists

    # --- Keep running or integrate with Godot loop ---
    print("\nRunning... Press Ctrl+C to exit.")
    # If not using godot-rl, you might need a loop here
    # import time
    # while True:
    #     time.sleep(1) # Keep script alive

except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print(f"\nAn error occurred: {e}")
finally:
    if connector:
        connector.disconnect()

```

## Godot Setup (Placeholder)

*   Instructions on setting up the Godot project side (e.g., required nodes, scripts for communication, VRM addon setup) need to be added here.
*   Ensure the Godot project listens on the correct port (default 9000 if not using `godot-rl`).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT-0 License