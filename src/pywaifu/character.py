# src/pywaifu/character.py
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .godot import GodotConnector, GodotError
from .utils import load_gemini_api_key, ApiKeyNotFoundError

# Define a custom error for LLM issues
class LLMError(Exception):
    """Custom exception for LLM related errors."""
    pass

class Character:
    """
    Represents an AI-powered character using Google Gemini.
    """
    # Define the model name to use
    GEMINI_MODEL_NAME = 'gemini-2.5-pro'

    def __init__(self, name: str, personality: str, godot_connector: GodotConnector = None):
        """
        Initializes the character using Google Gemini.

        Args:
            name: The character's name.
            personality: A description of the character's personality. This will be used
                         to construct the initial system instructions for the chat model.
            godot_connector: An instance of GodotConnector for Godot interaction.

        Raises:
            LLMError: If the API key cannot be loaded or the Gemini model fails to initialize.
        """
        self.name = name
        self.personality = personality
        self.godot_connector = godot_connector
        # self.context = [] # Replaced by Gemini's chat history
        self.state = {}

        try:
            # 1. Load API Key
            api_key = load_gemini_api_key()
            genai.configure(api_key=api_key)

            # 2. Define Safety Settings (Optional but Recommended)
            # Adjust these as needed for your application's tolerance
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            # 3. Initialize the Gemini Model
            # Add system instruction for personality
            system_instruction = (
                f"You are {self.name}. Your personality is: {self.personality}. "
                "Respond to the user naturally, embodying this personality. "
                "Keep your responses concise and conversational."
            )
            self.model = genai.GenerativeModel(
                model_name=self.GEMINI_MODEL_NAME,
                safety_settings=safety_settings,
                system_instruction=system_instruction
            )

            # 4. Start a Chat Session
            # The history will be managed by this chat object
            self.chat = self.model.start_chat(history=[])
            print(f"Gemini model '{self.GEMINI_MODEL_NAME}' initialized successfully for {self.name}.")

        except ApiKeyNotFoundError as e:
            raise LLMError(f"Failed to initialize Gemini: {e}") from e
        except Exception as e:
            # Catch other potential errors during genai setup
            raise LLMError(f"An unexpected error occurred during Gemini initialization: {e}") from e

        if godot_connector:
            self._register_callbacks()

    def talk(self, input_text: str) -> str:
        """
        Processes player input using the Gemini chat session and returns the response.

        Args:
            input_text: The text input from the player/user.

        Returns:
            The LLM's generated response string.

        Raises:
            LLMError: If there's an error during the API call or if the response is blocked.
        """
        if not self.chat:
            raise LLMError("Gemini chat session is not initialized.")

        print(f"Sending to Gemini: {input_text}") # Log input for debugging
        try:
            # Send the user message to the ongoing chat session
            response = self.chat.send_message(input_text)

            # Check for blocked content before accessing text
            if not response.candidates:
                 # If no candidates, likely blocked. Check prompt_feedback
                 block_reason = response.prompt_feedback.block_reason.name if response.prompt_feedback else "Unknown"
                 print(f"Warning: Gemini response potentially blocked. Reason: {block_reason}")
                 # Provide a generic response or raise an error
                 # return f"({self.name} seems hesitant to respond to that.)"
                 raise LLMError(f"Gemini response blocked. Reason: {block_reason}")

            # Extract the text from the first candidate
            # Accessing parts directly as response.text might raise an error if blocked
            generated_text = response.candidates[0].content.parts[0].text
            print(f"Received from Gemini: {generated_text}") # Log output for debugging
            return generated_text.strip()

        except Exception as e:
            # Catch potential API errors, connection issues, etc.
            print(f"Error during Gemini API call: {e}")
            raise LLMError(f"Error communicating with Gemini: {e}") from e

    def perform_action(self, action: str, *args) -> None:
        """Sends an action command to Godot."""
        if self.godot_connector:
            try:
                self.godot_connector.rpc(action, *args)
            except GodotError as e:
                 print(f"Warning: Failed to send action '{action}' to Godot: {e}")
                 # Decide if this should be a critical error or just a warning

    def update_state(self, state_updates: dict) -> None:
        """Updates the character's state."""
        self.state.update(state_updates)

    # _get_system_prompt is removed as personality is now part of system_instruction

    def _register_callbacks(self) -> None:
        """Registers callbacks with the Godot connector."""
        if self.godot_connector:
            # Assuming the Godot side sends an event named "player_input"
            # with the text data. Adjust the event name if necessary.
            # The callback now needs to handle potential data structure from Godot.
            def handle_player_input(event_data: dict):
                # Extract text, assuming it's under a 'text' key
                # Adjust this based on how Godot sends the data
                player_text = event_data.get("text", "")
                if player_text:
                    try:
                        response = self.talk(player_text)
                        # Send the response back to Godot (needs a defined mechanism)
                        # Example: self.godot_connector.rpc("display_character_response", response)
                        print(f"Processed player input via callback: {player_text} -> {response}")
                        # You'll need a way to send this 'response' back to Godot.
                        # This might involve another RPC call like:
                        if self.godot_connector:
                            self.godot_connector.rpc("character_spoke", self.name, response)
                    except LLMError as e:
                        print(f"LLM Error handling player input: {e}")
                        # Optionally send an error message back to Godot
                        if self.godot_connector:
                             self.godot_connector.rpc("character_error", self.name, str(e))
                    except GodotError as e:
                         print(f"Godot Error sending response back: {e}")
                else:
                    print("Received player_input event with no text.")

            self.godot_connector.register_callback("player_input", handle_player_input)
            print("Registered 'player_input' callback with Godot connector.")