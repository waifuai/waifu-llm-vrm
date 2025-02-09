# src/pywaifu/character.py

from .godot import GodotConnector
from .llm import LLMManager

class Character:
    """Represents an AI-powered character."""

    def __init__(self, name: str, personality: str, model: str = None, godot_connector: GodotConnector = None):
        """
        Initializes the character.
        """
        self.name = name
        self.personality = personality
        self.model = model
        self.godot_connector = godot_connector
        self.context = []
        self.state = {}
        self.llm_manager = LLMManager() #Now using our basic chatbot.
        if godot_connector:
            self._register_callbacks()

    def talk(self, input_text: str) -> str:
        """
        Processes player input, queries the LLM, and returns the response.
        """
        # No system prompt needed for the simple chatbot
        response = self.llm_manager.query(prompt=input_text)
        self.context = self.llm_manager.manage_context(input_text, self.context, 1000) #Add to context.
        return response

    def perform_action(self, action: str, *args) -> None:
        """Sends an action command to Godot."""
        if self.godot_connector:
            self.godot_connector.rpc(action, *args)

    def update_state(self, state_updates: dict) -> None:
        """Updates the character's state."""
        self.state.update(state_updates)

    def _get_system_prompt(self) -> str: #Not used.
        """Constructs the system prompt."""
        return ""

    def _register_callbacks(self) -> None:
        if self.godot_connector:
            self.godot_connector.register_callback("player_input", self.talk)