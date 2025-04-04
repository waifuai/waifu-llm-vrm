# tests/test_vrm.py
import unittest
from unittest.mock import MagicMock
from pywaifu.vrm import VRMCharacter
# from pywaifu.godot import GodotConnector # Mocking this

class TestVRMCharacter(unittest.TestCase):
    def setUp(self):
        """Set up a VRMCharacter instance with a mocked GodotConnector."""
        self.mock_godot_connector = MagicMock()
        self.vrm_node_path = "/root/vrm_node"
        self.vrm_character = VRMCharacter(
            name="TestVRM",
            personality="Animated",
            godot_connector=self.mock_godot_connector,
            vrm_node_path=self.vrm_node_path
        )

    def test_play_animation_calls_rpc(self):
        """Test that play_animation calls the correct RPC."""
        anim_name = "idle"
        blend_time = 0.2
        self.vrm_character.play_animation(anim_name, blend_time)
        self.mock_godot_connector.rpc.assert_called_once_with(
            "play_animation", self.vrm_node_path, anim_name, blend_time
        )

    def test_set_expression_calls_rpc(self):
        """Test that set_expression calls the correct RPC."""
        expr_name = "happy"
        value = 0.8
        self.vrm_character.set_expression(expr_name, value)
        self.mock_godot_connector.rpc.assert_called_once_with(
            "set_expression", self.vrm_node_path, expr_name, value
        )

    def test_get_animation_list_calls_rpc(self):
        """Test that get_animation_list calls the correct RPC and returns its result."""
        expected_list = ["idle", "walk", "run"]
        self.mock_godot_connector.rpc.return_value = expected_list # Mock the return value
        result = self.vrm_character.get_animation_list()
        self.mock_godot_connector.rpc.assert_called_once_with(
            "get_animation_list", self.vrm_node_path
        )
        self.assertEqual(result, expected_list)

    def test_get_blendshape_list_calls_rpc(self):
        """Test that get_blendshape_list calls the correct RPC and returns its result."""
        expected_list = ["neutral", "happy", "sad", "angry"]
        self.mock_godot_connector.rpc.return_value = expected_list # Mock the return value
        result = self.vrm_character.get_blendshape_list()
        self.mock_godot_connector.rpc.assert_called_once_with(
            "get_blendshape_list", self.vrm_node_path
        )
        self.assertEqual(result, expected_list)