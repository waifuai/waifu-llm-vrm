# tests/test_character.py
import unittest
from pywaifu.character import Character
from pywaifu.godot import GodotConnector
from pywaifu.llm import LLMManager

class TestCharacter(unittest.TestCase):
    def setUp(self):
        self.godot_connector = GodotConnector("path/to/godot/project")
        self.character = Character("Test", "Test", godot_connector=self.godot_connector)

    def test_talk(self):
        response = self.character.talk("hello")
        self.assertIsNotNone(response)

    def test_perform_action(self):
        self.character.perform_action("some_action") #Should not raise error.

    def test_update_state(self):
        self.character.update_state({"key": "value"})
        self.assertEqual(self.character.state["key"], "value")