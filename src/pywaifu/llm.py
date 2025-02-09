# src/pywaifu/llm.py

class LLMManager:
    """
    A very basic chatbot for testing purposes.  Does NOT use an actual LLM.
    """

    def __init__(self):
        self.responses = {
            "hello": "Hi there!",
            "how are you": "I'm doing well, thank you!",
            "what is your name": "I'm a simple chatbot.",
            "bye": "Goodbye!",
            "default": "I don't understand.",
        }

    def query(self, prompt: str, role: str = "user", system_prompt: str = None, context: list = None, model: str = None) -> str:
        """
        Returns a simple response based on the input.
        """
        # Convert to lowercase for case-insensitive matching
        prompt = prompt.lower()

        # Check if the prompt is in our predefined responses
        if prompt in self.responses:
            return self.responses[prompt]
        else:
            return self.responses["default"]

    def get_models(self) -> list:
        """Returns available models"""
        return ["default"]

    def set_model(self, model: str) -> None:
        """Sets model."""
        pass #Nothing to do.

    def manage_context(self, new_input: str, context:list, max_length:int)->list:
        """Manage context by simply appending to it."""
        context.append({"role": "user", "content": new_input})
        response = self.query(new_input)
        context.append({"role": "assistant", "content": response})
        return context

    def summarize_context(self, context:list) -> str:
      """Returns simple summary."""
      return "This is a basic chatbot conversation" #Simple.

    def _count_tokens(self, text:str)->int:
      """Counts tokens."""
      return len(text.split()) #Simple word count.
class LLMError(Exception):
  pass