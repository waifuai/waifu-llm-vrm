# tests/test_character.py
import unittest
from unittest.mock import MagicMock, patch
from pywaifu.character import Character
# Mock GodotConnector to avoid actual connection attempts during tests
# from pywaifu.godot import GodotConnector
# from pywaifu.llm import LLMManager # LLMManager is implicitly tested via Character

class TestCharacter(unittest.TestCase):
    def setUp(self):
        """Set up a Character instance with a mocked GodotConnector."""
        # Mock the GodotConnector to isolate Character logic
        self.mock_godot_connector = MagicMock()
        # self.mock_godot_connector.rpc = MagicMock() # Ensure rpc can be called

        # Initialize Character with the mock connector and default LLM (distilgpt2)
        # The LLMManager will be initialized inside Character
        self.character = Character(
            name="TestBot",
            personality="Helpful and curious",
            godot_connector=self.mock_godot_connector
            # model_name="distilgpt2" # Use default
            # context_max_tokens=512 # Use default
        )
        # Ensure the LLMManager was created (basic check)
        self.assertIsNotNone(self.character.llm_manager)

    def test_talk_generates_response(self):
        """Test that talk method returns a string response and updates context."""
        initial_context_len = len(self.character.context)
        prompt = "What is your favorite color?"
        response = self.character.talk(prompt)

        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0, "Response should not be empty")
        print(f"\nTest Talk: Prompt='{prompt}', Response='{response}'")

        # Check if context was updated (user prompt + assistant response = 2 turns)
        self.assertEqual(len(self.character.context), initial_context_len + 2)
        self.assertEqual(self.character.context[-2]["role"], "user")
        self.assertEqual(self.character.context[-2]["content"], prompt)
        self.assertEqual(self.character.context[-1]["role"], "assistant")
        self.assertEqual(self.character.context[-1]["content"], response)

    def test_perform_action_calls_godot_rpc(self):
        """Test that perform_action calls the GodotConnector's rpc method."""
        action_name = "wave"
        action_args = (1, "hello")
        self.character.perform_action(action_name, *action_args)

        # Verify that the mock connector's rpc method was called once with the correct arguments
        self.mock_godot_connector.rpc.assert_called_once_with(action_name, *action_args)

    def test_update_state_modifies_state_dict(self):
        """Test that update_state correctly modifies the internal state dictionary."""
        self.assertEqual(self.character.state, {}) # Initial state should be empty
        update_data = {"mood": "happy", "location": "lobby"}
        self.character.update_state(update_data)
        self.assertEqual(self.character.state, update_data)

        # Test updating existing keys
        more_updates = {"mood": "excited", "task": "greeting"}
        expected_state = {"mood": "excited", "location": "lobby", "task": "greeting"}
        self.character.update_state(more_updates)
        self.assertEqual(self.character.state, expected_state)

    def test_get_system_prompt_contains_details(self):
        """Test that the generated system prompt includes name and personality."""
        system_prompt = self.character._get_system_prompt()
        self.assertIn(self.character.name, system_prompt)
        self.assertIn(self.character.personality, system_prompt)