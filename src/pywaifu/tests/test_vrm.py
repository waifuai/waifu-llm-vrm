# tests/test_vrm.py
import unittest
from pywaifu.vrm import VRMCharacter
from pywaifu.godot import GodotConnector

class TestVRMCharacter(unittest.TestCase):
    def setUp(self):
        self.godot_connector = GodotConnector("path/to/godot/project")
        self.vrm_character = VRMCharacter("Test", "Test", godot_connector=self.godot_connector, vrm_node_path="/root/vrm_node")

    def test_play_animation(self):
        self.vrm_character.play_animation("idle")

    def test_set_expression(self):
        self.vrm_character.set_expression("happy", 0.5)

    def test_get_animation_list(self):
        #This test will fail since it needs to be run from Godot.
        self.vrm_character.get_animation_list()

    def test_get_blendshape_list(self):
        #This test will fail since it needs to be run from Godot.
        self.vrm_character.get_blendshape_list()