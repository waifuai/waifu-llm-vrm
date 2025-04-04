# src/pywaifu/character.py

from .godot import GodotConnector
from .llm import LLMManager

class Character:
    """Represents an AI-powered character."""

    def __init__(self, name: str, personality: str, model_name: str = None, godot_connector: GodotConnector = None, context_max_tokens: int = 512):
        """
        Initializes the character.

        Args:
            name: The character's name.
            personality: A description of the character's personality.
            model_name: The Hugging Face model name to use (defaults to LLMManager.DEFAULT_MODEL).
            godot_connector: An instance of GodotConnector for Godot interaction.
            context_max_tokens: The maximum number of tokens to keep in the conversation context.
        """
        self.name = name
        self.personality = personality
        self.godot_connector = godot_connector
        self.context = []
        self.state = {}
        self.context_max_tokens = context_max_tokens # Max tokens for context history
        self.llm_manager = LLMManager(model_name=model_name)
        if godot_connector:
            self._register_callbacks()

    def talk(self, input_text: str, max_new_tokens: int = 50) -> str:
        """
        Processes player input, queries the LLM, manages context, and returns the response.

        Args:
            input_text: The text input from the player/user.
            max_new_tokens: The maximum number of tokens for the LLM to generate.

        Returns:
            The LLM's generated response string.
        """
        system_prompt = self._get_system_prompt()
        response = self.llm_manager.query(
            prompt=input_text,
            system_prompt=system_prompt,
            context=self.context,
            max_new_tokens=max_new_tokens
        )
        # Update context after getting the response
        self.context = self.llm_manager.manage_context(
            new_input=input_text,
            new_response=response,
            context=self.context,
            max_tokens=self.context_max_tokens
        )
        return response

    def perform_action(self, action: str, *args) -> None:
        """Sends an action command to Godot."""
        if self.godot_connector:
            self.godot_connector.rpc(action, *args)

    def update_state(self, state_updates: dict) -> None:
        """Updates the character's state."""
        self.state.update(state_updates)

    def _get_system_prompt(self) -> str:
        """Constructs the system prompt based on character details."""
        # Keep it concise for smaller models like distilgpt2
        return f"You are {self.name}. Your personality is: {self.personality}. Respond to the user naturally."

    def _register_callbacks(self) -> None:
        if self.godot_connector:
            self.godot_connector.register_callback("player_input", self.talk)