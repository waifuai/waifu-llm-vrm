# tests/test_vrm.py
import unittest
from unittest.mock import MagicMock, patch, ANY
from pywaifu.vrm import VRMCharacter
# Import Character to access GEMINI_MODEL_NAME if needed, and errors
from pywaifu.character import Character, LLMError
from pywaifu.utils import ApiKeyNotFoundError
# from pywaifu.godot import GodotConnector # Mocking this

# Patch Gemini dependencies needed for the parent Character class initialization
@patch('pywaifu.character.genai.GenerativeModel')
@patch('pywaifu.character.genai.configure')
@patch('pywaifu.character.load_gemini_api_key')
class TestVRMCharacter(unittest.TestCase):
    def setUp(self, mock_load_key, mock_configure, mock_genai_model):
        """Set up a VRMCharacter instance with mocked GodotConnector and Gemini deps."""
        # Configure mocks for Gemini initialization (needed by parent class)
        mock_load_key.return_value = "DUMMY_API_KEY"
        mock_model_instance = MagicMock()
        mock_chat_session = MagicMock()
        mock_model_instance.start_chat.return_value = mock_chat_session
        mock_genai_model.return_value = mock_model_instance

        # Mock the GodotConnector
        self.mock_godot_connector = MagicMock()
        self.vrm_node_path = "/root/vrm_node"

        # Initialize VRMCharacter - remove the 'model' parameter which no longer exists
        # The Gemini setup happens in the parent Character.__init__
        self.vrm_character = VRMCharacter(
            name="TestVRM",
            personality="Animated",
            godot_connector=self.mock_godot_connector,
            vrm_node_path=self.vrm_node_path
            # No model_name or model parameter here anymore
        )

        # Store mocks if needed for assertions (though likely not needed for VRM tests)
        self.mock_load_key = mock_load_key
        self.mock_configure = mock_configure
        self.mock_genai_model = mock_genai_model
        self.mock_model_instance = mock_model_instance
        self.mock_chat_session = mock_chat_session


    # The following tests focus on VRM RPC calls and don't need the Gemini mocks directly,
    # but the mocks in setUp ensure the object initializes correctly.
    # They also don't need the mock arguments passed in.

    def test_play_animation_calls_rpc(self, *mocks): # Use *mocks to absorb patched args
        """Test that play_animation calls the correct RPC."""
        anim_name = "idle"
        blend_time = 0.2
        self.vrm_character.play_animation(anim_name, blend_time)
        self.mock_godot_connector.rpc.assert_called_once_with(
            "play_animation", self.vrm_node_path, anim_name, blend_time
        )

    def test_set_expression_calls_rpc(self, *mocks):
        """Test that set_expression calls the correct RPC."""
        expr_name = "happy"
        value = 0.8
        self.vrm_character.set_expression(expr_name, value)
        self.mock_godot_connector.rpc.assert_called_once_with(
            "set_expression", self.vrm_node_path, expr_name, value
        )

    def test_get_animation_list_calls_rpc(self, *mocks):
        """Test that get_animation_list calls the correct RPC and returns its result."""
        expected_list = ["idle", "walk", "run"]
        # Reset mock for this specific test if needed, or ensure setup provides fresh mock
        self.mock_godot_connector.rpc.reset_mock()
        self.mock_godot_connector.rpc.return_value = expected_list # Mock the return value
        result = self.vrm_character.get_animation_list()
        self.mock_godot_connector.rpc.assert_called_once_with(
            "get_animation_list", self.vrm_node_path
        )
        self.assertEqual(result, expected_list)

    def test_get_blendshape_list_calls_rpc(self, *mocks):
        """Test that get_blendshape_list calls the correct RPC and returns its result."""
        expected_list = ["neutral", "happy", "sad", "angry"]
        # Reset mock for this specific test
        self.mock_godot_connector.rpc.reset_mock()
        self.mock_godot_connector.rpc.return_value = expected_list # Mock the return value
        result = self.vrm_character.get_blendshape_list()
        self.mock_godot_connector.rpc.assert_called_once_with(
            "get_blendshape_list", self.vrm_node_path
        )
        self.assertEqual(result, expected_list)

    def test_play_animation_without_godot_connector(self, *mocks):
        """Test that play_animation handles missing Godot connector gracefully."""
        vrm_no_connector = VRMCharacter(
            name="TestVRM",
            personality="Test",
            vrm_node_path=self.vrm_node_path
        )
        # Should not raise an exception
        vrm_no_connector.play_animation("test_anim", 0.5)

    def test_set_expression_without_godot_connector(self, *mocks):
        """Test that set_expression handles missing Godot connector gracefully."""
        vrm_no_connector = VRMCharacter(
            name="TestVRM",
            personality="Test",
            vrm_node_path=self.vrm_node_path
        )
        # Should not raise an exception
        vrm_no_connector.set_expression("happy", 0.8)

    def test_play_animation_with_godot_error(self, *mocks):
        """Test that play_animation handles Godot errors gracefully."""
        from pywaifu.godot import GodotError
        self.mock_godot_connector.rpc.side_effect = GodotError("Connection failed")

        # Should not raise an exception, just print warning
        self.vrm_character.play_animation("test_anim", 0.5)
        self.mock_godot_connector.rpc.assert_called_once()

    def test_set_expression_with_godot_error(self, *mocks):
        """Test that set_expression handles Godot errors gracefully."""
        from pywaifu.godot import GodotError
        self.mock_godot_connector.rpc.side_effect = GodotError("Connection failed")

        # Should not raise an exception, just print warning
        self.vrm_character.set_expression("happy", 0.8)
        self.mock_godot_connector.rpc.assert_called_once()

    def test_get_animation_list_with_godot_error(self, *mocks):
        """Test that get_animation_list handles Godot errors gracefully."""
        from pywaifu.godot import GodotError
        self.mock_godot_connector.rpc.side_effect = GodotError("Connection failed")

        result = self.vrm_character.get_animation_list()
        self.assertEqual(result, [])
        self.mock_godot_connector.rpc.assert_called_once()

    def test_get_blendshape_list_with_godot_error(self, *mocks):
        """Test that get_blendshape_list handles Godot errors gracefully."""
        from pywaifu.godot import GodotError
        self.mock_godot_connector.rpc.side_effect = GodotError("Connection failed")

        result = self.vrm_character.get_blendshape_list()
        self.assertEqual(result, [])
        self.mock_godot_connector.rpc.assert_called_once()

    def test_play_animation_with_zero_blend_time(self, *mocks):
        """Test that play_animation works with zero blend time."""
        self.vrm_character.play_animation("test_anim", 0.0)
        self.mock_godot_connector.rpc.assert_called_once_with(
            "play_animation", self.vrm_node_path, "test_anim", 0.0
        )

    def test_set_expression_with_extreme_values(self, *mocks):
        """Test that set_expression handles extreme values."""
        # Test with value 0.0
        self.mock_godot_connector.rpc.reset_mock()
        self.vrm_character.set_expression("neutral", 0.0)
        self.mock_godot_connector.rpc.assert_called_once_with(
            "set_expression", self.vrm_node_path, "neutral", 0.0
        )

        # Test with value 1.0
        self.mock_godot_connector.rpc.reset_mock()
        self.vrm_character.set_expression("happy", 1.0)
        self.mock_godot_connector.rpc.assert_called_once_with(
            "set_expression", self.vrm_node_path, "happy", 1.0
        )

    def test_vrm_character_inherits_from_character(self, *mocks):
        """Test that VRMCharacter properly inherits from Character."""
        self.assertTrue(hasattr(self.vrm_character, 'name'))
        self.assertTrue(hasattr(self.vrm_character, 'personality'))
        self.assertTrue(hasattr(self.vrm_character, 'talk'))
        self.assertTrue(hasattr(self.vrm_character, 'state'))
        self.assertEqual(self.vrm_character.name, "TestVRM")
        self.assertEqual(self.vrm_character.personality, "Animated")

if __name__ == '__main__':
    unittest.main()