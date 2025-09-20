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

## Godot Setup

To integrate pywaifu with your Godot project:

### Basic Setup

1. **Create a Godot Project**: Start a new Godot project or use an existing one.

2. **Network Configuration**:
   - If using `godot-rl`: Ensure godot-rl is properly configured in your Godot project.
   - If using sockets: Make sure your Godot project listens on port 9000 (default) or the port specified in your configuration.

3. **Communication Scripts**:
   You'll need to implement Godot scripts to handle RPC calls from Python. Add these methods to your Godot nodes:
   - `play_animation(node_path, animation_name, blend_time)`
   - `set_expression(node_path, expression_name, value)`
   - `get_animation_list(node_path)`
   - `get_blendshape_list(node_path)`
   - `character_spoke(character_name, message)`
   - `character_error(character_name, error_message)`

### VRM Setup (Optional)

If you want to use VRM characters with animations and expressions:

1. **Install VRM Addon**: Add a VRM-compatible addon to your Godot project.

2. **Model Import**: Import your VRM model into Godot and note the node path.

3. **Animation Setup**: Ensure your VRM model has animation player with animations like "Wave", "Idle", etc.

4. **Blend Shapes**: Set up blend shapes for expressions like "Happy", "Sad", "Neutral", etc.

### Example Godot Script

```gdscript
extends Node

func _ready():
    # Start listening for connections
    var server = TCP_Server.new()
    server.listen(9000, "127.0.0.1")

func play_animation(node_path, animation_name, blend_time):
    var vrm_node = get_node(node_path)
    if vrm_node and vrm_node.has_method("play"):
        vrm_node.play(animation_name)

func set_expression(node_path, expression_name, value):
    var vrm_node = get_node(node_path)
    if vrm_node and vrm_node.has_method("set_blend_shape"):
        vrm_node.set_blend_shape(expression_name, value)

func get_animation_list(node_path):
    var vrm_node = get_node(node_path)
    if vrm_node and vrm_node.has_method("get_animation_list"):
        return vrm_node.get_animation_list()
    return []

func get_blendshape_list(node_path):
    var vrm_node = get_node(node_path)
    if vrm_node and vrm_node.has_method("get_blendshape_list"):
        return vrm_node.get_blendshape_list()
    return []
```

## API Reference

### Character Class

The main class for creating AI characters.

#### Constructor
```python
Character(name: str, personality: str, godot_connector: GodotConnector = None)
```

#### Methods

- `talk(input_text: str) -> str`: Send user input to the character and get a response
- `perform_action(action: str, *args) -> None`: Send an action command to Godot
- `update_state(state_updates: dict) -> None`: Update the character's internal state

### VRMCharacter Class

Extended character class with VRM animation support.

#### Constructor
```python
VRMCharacter(name: str, personality: str, godot_connector: GodotConnector = None, vrm_node_path: str = None)
```

#### Additional Methods

- `play_animation(animation_name: str, blend_time: float = 0.0) -> None`: Play a VRM animation
- `set_expression(expression_name: str, value: float) -> None`: Set a VRM blend shape value
- `get_animation_list() -> list`: Get list of available animations from Godot
- `get_blendshape_list() -> list`: Get list of available blend shapes from Godot

### GodotConnector Class

Handles communication between Python and Godot.

#### Constructor
```python
GodotConnector(project_path: str, port: int = None, auto_start: bool = True, headless: bool = True)
```

#### Methods

- `connect() -> None`: Establish connection to Godot
- `disconnect() -> None`: Close the connection
- `rpc(func_name: str, *args) -> any`: Call a function in Godot
- `register_callback(event: str, callback: callable) -> None`: Register a callback for Godot events

## Troubleshooting

### Common Issues

1. **"Could not connect to Godot" Error**
   - Ensure Godot is running and listening on the correct port
   - Check that your Godot project has the necessary network scripts
   - Verify the project path is correct

2. **"API key file not found" Error**
   - Create the `~/.api-gemini` file
   - Ensure the file contains only your Google Gemini API key
   - Check file permissions

3. **VRM animations not working**
   - Verify the VRM node path is correct
   - Ensure the VRM model has the required animations
   - Check that blend shapes are properly set up

4. **Poor performance**
   - Reduce conversation history by implementing context limits
   - Use shorter personality descriptions
   - Consider using a simpler Gemini model if available

### Debug Mode

Enable debug logging by setting the logging level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Advanced Character with Custom Behavior

```python
from pywaifu import Character, GodotConnector
import time

class CustomCharacter(Character):
    def __init__(self, name, personality, **kwargs):
        super().__init__(name, personality, **kwargs)
        self.interaction_count = 0

    def talk(self, input_text):
        self.interaction_count += 1
        response = super().talk(input_text)

        # Add custom behavior based on interaction count
        if self.interaction_count % 5 == 0:
            response += " (This is our 5th conversation! How can I assist you better?)"

        return response

# Usage
connector = GodotConnector("path/to/godot/project")
character = CustomCharacter(
    name="Assistant",
    personality="Helpful and knowledgeable AI assistant",
    godot_connector=connector
)

connector.connect()
print("Character ready! Type 'quit' to exit.")

while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        break

    response = character.talk(user_input)
    print(f"{character.name}: {response}")

connector.disconnect()
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src/pywaifu

# Run specific test file
python -m pytest src/pywaifu/tests/test_character.py
```

### Project Structure

```
pywaifu/
├── src/
│   └── pywaifu/
│       ├── __init__.py          # Package initialization
│       ├── character.py         # Main Character class
│       ├── vrm.py              # VRMCharacter class
│       ├── godot.py            # GodotConnector class
│       ├── utils.py            # Utility functions
│       └── tests/              # Test files
│           ├── __init__.py
│           ├── test_character.py
│           ├── test_vrm.py
│           └── test_godot.py
├── examples/                   # Usage examples
│   └── basic_usage.py
├── README.md                   # Project documentation
├── requirements.txt           # Python dependencies
├── pytest.ini                # Test configuration
└── .gitignore                # Git ignore patterns
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code:
- Follows PEP 8 style guidelines
- Includes tests for new functionality
- Updates documentation as needed
- Passes all existing tests

## License

MIT-0 License

## Changelog

### Version 1.0.0
- Initial release
- Basic Character class with Gemini integration
- VRMCharacter class for VRM model support
- GodotConnector for Godot communication
- Comprehensive test suite
- Documentation and examples