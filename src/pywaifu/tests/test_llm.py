# tests/test_llm.py
import unittest
from pywaifu.llm import LLMManager

class TestLLMManager(unittest.TestCase):

    def setUp(self):
        self.manager = LLMManager()

    def test_query(self):
        self.assertEqual(self.manager.query("hello"), "Hi there!")
        self.assertEqual(self.manager.query("How are you"), "I'm doing well, thank you!")
        self.assertEqual(self.manager.query("unknown"), "I don't understand.")
        self.assertEqual(self.manager.query("HELLO"), "Hi there!") # Case-insensitive

    def test_context_management(self):
        context = []
        context = self.manager.manage_context("hello", context, 100)
        self.assertEqual(len(context), 2) # Check context.

    def test_get_models(self):
        self.assertEqual(self.manager.get_models(), ["default"])

    def test_set_models(self):
        self.manager.set_model("something") # Should not raise error.

    def test_summarize_context(self):
        self.assertEqual(self.manager.summarize_context([]), "This is a basic chatbot conversation")

    def test_count_tokens(self):
        self.assertEqual(self.manager._count_tokens("hello world"), 2)

if __name__ == '__main__':
    unittest.main()