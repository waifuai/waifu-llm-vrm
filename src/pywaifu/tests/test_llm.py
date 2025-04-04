# tests/test_llm.py
import unittest
import time # Import time for potential delays in model loading
from pywaifu.llm import LLMManager, LLMError

# Consider adding mocking later if tests become too slow/resource intensive
# from unittest.mock import patch, MagicMock

class TestLLMManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load the model once for all tests in this class."""
        print("\nSetting up TestLLMManager: Loading model (this may take a moment)...")
        start_time = time.time()
        try:
            # Use the default model (distilgpt2) for tests
            cls.manager = LLMManager()
            print(f"Model loaded successfully in {time.time() - start_time:.2f} seconds.")
        except LLMError as e:
            print(f"Failed to load model during setup: {e}")
            cls.manager = None # Ensure manager is None if setup fails
        except Exception as e:
            print(f"An unexpected error occurred during model loading: {e}")
            cls.manager = None


    def setUp(self):
        """Ensure the manager was loaded."""
        if self.manager is None:
            self.skipTest("LLMManager setup failed, skipping test.")
        # Reset context for each test if needed (though LLMManager doesn't store context internally)

    def test_query_basic(self):
        """Test basic query functionality."""
        prompt = "Hello, how are you?"
        response = self.manager.query(prompt)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0, "Response should not be empty")
        print(f"\nTest Query Basic: Prompt='{prompt}', Response='{response}'")

    def test_query_with_context(self):
        """Test query with conversation history."""
        context = [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."}
        ]
        prompt = "What is its population?"
        response = self.manager.query(prompt, context=context)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        # We expect the model to potentially use the context (Paris)
        print(f"\nTest Query Context: Prompt='{prompt}', Response='{response}'")
        # Check if 'Paris' or population related terms are mentioned (optional, model dependent)
        # self.assertTrue("paris" in response.lower() or "million" in response.lower())

    def test_query_with_system_prompt(self):
        """Test query with a system prompt."""
        system_prompt = "You are a helpful pirate assistant."
        prompt = "Where can I find treasure?"
        response = self.manager.query(prompt, system_prompt=system_prompt)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        print(f"\nTest Query System Prompt: Prompt='{prompt}', Response='{response}'")
        # Check for pirate-like language (optional, model dependent)
        # self.assertTrue("arr" in response.lower() or "matey" in response.lower())

    def test_manage_context_append(self):
        """Test adding turns to context."""
        context = []
        context = self.manager.manage_context("Hi", "Hello there!", context, 100)
        self.assertEqual(len(context), 2)
        self.assertEqual(context[0]["role"], "user")
        self.assertEqual(context[0]["content"], "Hi")
        self.assertEqual(context[1]["role"], "assistant")
        self.assertEqual(context[1]["content"], "Hello there!")

    def test_manage_context_truncation(self):
        """Test context truncation based on max_tokens."""
        # Use estimated token counts for simplicity
        context = [
            {"role": "user", "content": "This is the first long message."}, # ~6 tokens
            {"role": "assistant", "content": "Okay, I understand the first message."}, # ~7 tokens
            {"role": "user", "content": "This is the second long message."}, # ~6 tokens
            {"role": "assistant", "content": "Okay, I understand the second message."} # ~7 tokens
        ] # Total ~ 26 tokens
        max_tokens = 20 # Set max tokens lower than current context

        # Add a new turn that should trigger truncation
        new_input = "Short input" # ~2 tokens
        new_response = "Short response" # ~2 tokens
        # Expected total before truncation: 26 + 2 + 2 = 30 tokens

        updated_context = self.manager.manage_context(new_input, new_response, context, max_tokens)

        # Expect the first turn (user + assistant) to be removed (6 + 7 = 13 tokens removed)
        # Expected final tokens = 30 - 13 = 17 (which is <= max_tokens)
        self.assertEqual(len(updated_context), 2) # Should have removed the first two pairs (4 entries)
        # After truncation removed the first 4 entries, the remaining 2 should be the new ones
        self.assertEqual(updated_context[0]["role"], "user")
        self.assertEqual(updated_context[0]["content"], new_input)
        self.assertEqual(updated_context[1]["role"], "assistant")
        self.assertEqual(updated_context[1]["content"], new_response)
        # Verify token count is roughly within limits (allow some buffer for encoding differences)
        final_tokens = sum(self.manager._count_tokens(f"{turn['role']}: {turn['content']}") for turn in updated_context)
        self.assertLessEqual(final_tokens, max_tokens + 5) # Allow a small margin

    def test_get_models(self):
        """Test retrieving the model name."""
        models = self.manager.get_models()
        self.assertIsInstance(models, list)
        self.assertIn(self.manager.model_name, models) # Should contain the loaded model

    # @unittest.skip("Skipping set_model test as it re-initializes and can be slow/resource intensive.")
    def test_set_model(self):
        """Test switching models (re-initializes)."""
        original_model = self.manager.model_name
        # Note: This will actually load the new model, which might be slow.
        # Consider mocking if this becomes an issue.
        # Using the same model to avoid extra downloads during test run.
        new_model_name = original_model
        try:
            self.manager.set_model(new_model_name)
            self.assertEqual(self.manager.model_name, new_model_name)
            # Perform a basic query to ensure the new setup works
            response = self.manager.query("Test query after set_model")
            self.assertIsInstance(response, str)
        finally:
            # Optionally switch back if needed, though setUpClass handles fresh instance
            if self.manager.model_name != original_model:
                 print(f"\nSwitching model back to {original_model}")
                 self.manager.set_model(original_model)

    def test_summarize_context(self):
        """Test context summarization."""
        context_empty = []
        summary_empty = self.manager.summarize_context(context_empty)
        self.assertIn("conversation has not started", summary_empty.lower())

        context_filled = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        summary_filled = self.manager.summarize_context(context_filled)
        self.assertIn("2 turns", summary_filled)
        self.assertIn("Hello", summary_filled) # Check if last user message is mentioned

    def test_count_tokens(self):
        """Test token counting."""
        # Exact token count depends on the tokenizer, check for reasonable integer output
        text = "This is a test sentence."
        token_count = self.manager._count_tokens(text)
        self.assertIsInstance(token_count, int)
        self.assertGreater(token_count, 0)
        # For distilgpt2, "This is a test sentence." should be more than 1 token
        self.assertGreater(token_count, 1)
        print(f"\nTest Count Tokens: Text='{text}', Tokens={token_count}")

if __name__ == '__main__':
    unittest.main()