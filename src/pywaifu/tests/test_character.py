# tests/test_character.py
import unittest
from unittest.mock import MagicMock, patch, ANY
# Import Character and the custom errors
from pywaifu.character import Character, LLMError
from pywaifu.utils import ApiKeyNotFoundError
# Mock GodotConnector to avoid actual connection attempts during tests
# from pywaifu.godot import GodotConnector, GodotError # Import GodotError if needed for testing error handling

# Define a dummy response structure similar to Gemini's
class MockGeminiPart:
    def __init__(self, text):
        self.text = text

class MockGeminiContent:
    def __init__(self, text):
        self.parts = [MockGeminiPart(text)]

class MockGeminiCandidate:
    def __init__(self, text):
        self.content = MockGeminiContent(text)

class MockGeminiResponse:
    def __init__(self, text="Default mock response", candidates=None, prompt_feedback=None):
        if candidates is None:
             # If text is provided, create a default candidate
             self.candidates = [MockGeminiCandidate(text)] if text else []
        else:
             self.candidates = candidates # Allow passing custom candidates (e.g., empty list for blocked)
        self.prompt_feedback = prompt_feedback # To simulate blocked responses

    # Add .text property for convenience if needed, mimicking successful response access
    @property
    def text(self):
        if self.candidates and self.candidates[0].content.parts:
            return self.candidates[0].content.parts[0].text
        # Raise error similar to Gemini if no valid text part
        raise ValueError("Response does not contain text.")


# Use patch decorators at the class level for broader scope
@patch('pywaifu.character.genai.GenerativeModel')
@patch('pywaifu.character.genai.configure')
@patch('pywaifu.character.load_gemini_api_key')
class TestCharacter(unittest.TestCase):

    def setUp(self, mock_load_key, mock_configure, mock_genai_model):
        """Set up a Character instance with mocked dependencies."""
        # Configure mocks before Character initialization
        mock_load_key.return_value = "DUMMY_API_KEY"

        # Mock the GenerativeModel instance and its start_chat method
        self.mock_model_instance = MagicMock()
        self.mock_chat_session = MagicMock()
        self.mock_model_instance.start_chat.return_value = self.mock_chat_session
        mock_genai_model.return_value = self.mock_model_instance

        # Mock the GodotConnector
        self.mock_godot_connector = MagicMock()
        # self.mock_godot_connector.rpc = MagicMock() # Ensure rpc can be called if needed

        # Initialize Character - model_name is no longer needed
        self.character = Character(
            name="TestBot",
            personality="Helpful and curious",
            godot_connector=self.mock_godot_connector
        )

        # Store mocks for potential assertions in tests
        self.mock_load_key = mock_load_key
        self.mock_configure = mock_configure
        self.mock_genai_model = mock_genai_model


    def test_init_configures_gemini(self, mock_load_key, mock_configure, mock_genai_model):
        """Test that __init__ configures Gemini correctly."""
        # Assertions are implicitly checked by setUp running without error,
        # but we can be more explicit.
        mock_load_key.assert_called_once()
        mock_configure.assert_called_once_with(api_key="DUMMY_API_KEY")
        # Check that GenerativeModel was called with model name and system instruction
        expected_system_instruction = (
            f"You are {self.character.name}. Your personality is: {self.character.personality}. "
            "Respond to the user naturally, embodying this personality. "
            "Keep your responses concise and conversational."
        )
        mock_genai_model.assert_called_once_with(
            model_name=Character.GEMINI_MODEL_NAME,
            safety_settings=ANY, # Or assert specific safety settings if needed
            system_instruction=expected_system_instruction
        )
        self.mock_model_instance.start_chat.assert_called_once_with(history=[])
        self.assertIsNotNone(self.character.model)
        self.assertIsNotNone(self.character.chat)

    def test_talk_sends_message_and_returns_response(self, mock_load_key, mock_configure, mock_genai_model):
        """Test that talk method sends input to Gemini and returns the text response."""
        prompt = "What is your favorite color?"
        expected_response_text = "My favorite color is blue!"
        # Configure the mock chat session to return a mock response
        self.mock_chat_session.send_message.return_value = MockGeminiResponse(text=expected_response_text)

        response = self.character.talk(prompt)

        # Verify send_message was called correctly
        self.mock_chat_session.send_message.assert_called_once_with(prompt)
        # Verify the response is the text part of the mock response
        self.assertEqual(response, expected_response_text)

    def test_talk_handles_llm_error(self, mock_load_key, mock_configure, mock_genai_model):
        """Test that talk method raises LLMError if Gemini call fails."""
        prompt = "This will cause an error."
        # Configure the mock chat session to raise an exception
        self.mock_chat_session.send_message.side_effect = Exception("Gemini API unavailable")

        with self.assertRaises(LLMError) as cm:
            self.character.talk(prompt)
        self.assertIn("Error communicating with Gemini", str(cm.exception))
        self.assertIn("Gemini API unavailable", str(cm.exception.__cause__))

    def test_talk_handles_blocked_response(self, mock_load_key, mock_configure, mock_genai_model):
        """Test that talk method raises LLMError if the response is blocked."""
        prompt = "Tell me something inappropriate."
        # Simulate a blocked response (no candidates)
        mock_blocked_feedback = MagicMock()
        mock_blocked_feedback.block_reason.name = "SAFETY"
        self.mock_chat_session.send_message.return_value = MockGeminiResponse(candidates=[], prompt_feedback=mock_blocked_feedback)

        with self.assertRaises(LLMError) as cm:
            self.character.talk(prompt)
        self.assertIn("Gemini response blocked. Reason: SAFETY", str(cm.exception))


    def test_perform_action_calls_godot_rpc(self, mock_load_key, mock_configure, mock_genai_model):
        """Test that perform_action calls the GodotConnector's rpc method."""
        action_name = "wave"
        action_args = (1, "hello")
        self.character.perform_action(action_name, *action_args)

        # Verify that the mock connector's rpc method was called once
        self.mock_godot_connector.rpc.assert_called_once_with(action_name, *action_args)

    def test_update_state_modifies_state_dict(self, mock_load_key, mock_configure, mock_genai_model):
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

    def test_talk_with_empty_input(self, mock_load_key, mock_configure, mock_genai_model):
        """Test that talk method handles empty input gracefully."""
        expected_response = "I'm here to help!"
        self.mock_chat_session.send_message.return_value = MockGeminiResponse(text=expected_response)

        response = self.character.talk("")
        self.assertEqual(response, expected_response)
        self.mock_chat_session.send_message.assert_called_once_with("")

    def test_talk_with_long_input(self, mock_load_key, mock_configure, mock_genai_model):
        """Test that talk method handles long input."""
        long_input = "a" * 1000
        expected_response = "That's a lot of a's!"
        self.mock_chat_session.send_message.return_value = MockGeminiResponse(text=expected_response)

        response = self.character.talk(long_input)
        self.assertEqual(response, expected_response)
        self.mock_chat_session.send_message.assert_called_once_with(long_input)

    def test_perform_action_without_godot_connector(self, mock_load_key, mock_configure, mock_genai_model):
        """Test that perform_action handles missing Godot connector gracefully."""
        # Create character without Godot connector
        character_no_godot = Character(name="TestBot", personality="Test personality")

        # Should not raise an exception
        character_no_godot.perform_action("test_action", "arg1", "arg2")

    def test_perform_action_with_godot_error(self, mock_load_key, mock_configure, mock_genai_model):
        """Test that perform_action handles Godot errors gracefully."""
        from pywaifu.godot import GodotError
        self.mock_godot_connector.rpc.side_effect = GodotError("Connection failed")

        # Should not raise an exception, just print warning
        self.character.perform_action("test_action", "arg1", "arg2")
        self.mock_godot_connector.rpc.assert_called_once_with("test_action", "arg1", "arg2")

    def test_talk_preserves_conversation_context(self, mock_load_key, mock_configure, mock_genai_model):
        """Test that multiple talk calls maintain conversation context."""
        responses = ["Hello!", "How are you?", "Nice to meet you!"]

        for i, expected_response in enumerate(responses):
            self.mock_chat_session.send_message.return_value = MockGeminiResponse(text=expected_response)
            response = self.character.talk(f"Message {i+1}")
            self.assertEqual(response, expected_response)

        self.assertEqual(self.mock_chat_session.send_message.call_count, 3)

    def test_character_initialization_with_empty_name(self, mock_load_key, mock_configure, mock_genai_model):
        """Test character initialization with edge case inputs."""
        # Test with empty personality
        character = Character(name="Test", personality="")
        self.assertEqual(character.name, "Test")
        self.assertEqual(character.personality, "")

        # Test with very long name
        long_name = "a" * 100
        character_long_name = Character(name=long_name, personality="Test")
        self.assertEqual(character_long_name.name, long_name)

    # test_get_system_prompt_contains_details is removed as _get_system_prompt no longer exists

if __name__ == '__main__':
    unittest.main()