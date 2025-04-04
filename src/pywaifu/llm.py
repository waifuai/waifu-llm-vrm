# src/pywaifu/llm.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class LLMManager:
    """
    Manages interaction with a Hugging Face language model.
    """

    DEFAULT_MODEL = "distilgpt2"

    def __init__(self, model_name: str = None):
        """
        Initializes the LLMManager, loading the specified model and tokenizer.

        Args:
            model_name: The name of the Hugging Face model to load (e.g., "distilgpt2").
                        Defaults to DEFAULT_MODEL.
        """
        self.model_name = model_name if model_name else self.DEFAULT_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            # Add pad token if missing (like in GPT-2)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
            # Use pipeline for easier text generation
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device,
                pad_token_id=self.tokenizer.eos_token_id # Set pad_token_id for pipeline
            )
        except Exception as e:
            raise LLMError(f"Failed to load model or tokenizer '{self.model_name}': {e}")

    def query(self, prompt: str, role: str = "user", system_prompt: str = None, context: list = None, max_new_tokens: int = 50) -> str:
        """
        Generates a response using the loaded language model.

        Args:
            prompt: The user's input prompt.
            role: The role of the prompt (currently unused but kept for potential future use).
            system_prompt: An initial system message to guide the model (prepended).
            context: A list of previous conversation turns (dicts with 'role' and 'content').
            max_new_tokens: The maximum number of new tokens to generate.

        Returns:
            The generated response string.
        """
        full_prompt = ""
        if system_prompt:
            full_prompt += system_prompt + "\n\n" # Add spacing

        if context:
            for turn in context:
                # Simple formatting for context
                full_prompt += f"{turn['role'].capitalize()}: {turn['content']}\n"

        # Add the current user prompt
        full_prompt += f"{role.capitalize()}: {prompt}\nAssistant:" # Prompt the model to respond as Assistant

        try:
            # Generate response using the pipeline
            # We pass the full prompt and ask for max_length = current_tokens + new_tokens
            # Note: max_length includes the prompt length.
            input_token_count = self._count_tokens(full_prompt)
            max_length = input_token_count + max_new_tokens

            # Use do_sample=True for more creative responses, add temperature if desired
            generated = self.generator(
                full_prompt,
                max_length=max_length,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7,
                top_k=50
                # pad_token_id=self.tokenizer.eos_token_id # Already set in pipeline init
            )

            # Extract only the newly generated text after the prompt
            response = generated[0]['generated_text'][len(full_prompt):].strip()

            # Clean up potential artifacts or incomplete sentences if needed
            # (e.g., remove partial lines, stop at sentence boundaries)
            # For now, just return the stripped response.
            return response

        except Exception as e:
            raise LLMError(f"Error during model query: {e}")

    def get_models(self) -> list:
        """Returns available models (currently just the loaded one)."""
        # In a more complex scenario, this could query Hugging Face Hub or a local cache
        return [self.model_name]

    def set_model(self, model: str) -> None:
        """Sets model (requires re-initialization)."""
        # For simplicity, we'll just re-initialize. A more robust implementation
        # might cache models or handle this differently.
        print(f"Switching model to: {model}. Re-initializing LLMManager.")
        self.__init__(model_name=model)


    def manage_context(self, new_input: str, new_response: str, context: list, max_tokens: int) -> list:
        """
        Manages the conversation context, adding new turns and truncating if necessary.

        Args:
            new_input: The latest user input.
            new_response: The latest assistant response.
            context: The current list of conversation turns.
            max_tokens: The maximum total tokens allowed for the context.

        Returns:
            The updated context list.
        """
        updated_context = context + [
            {"role": "user", "content": new_input},
            {"role": "assistant", "content": new_response}
        ]

        # Calculate total tokens and truncate if needed (simple FIFO for now)
        total_tokens = sum(self._count_tokens(f"{turn['role']}: {turn['content']}") for turn in updated_context)

        while total_tokens > max_tokens and len(updated_context) > 1:
            # Remove the oldest turn (user + assistant pair)
            removed_user = updated_context.pop(0)
            removed_assistant = updated_context.pop(0)
            total_tokens -= self._count_tokens(f"{removed_user['role']}: {removed_user['content']}")
            total_tokens -= self._count_tokens(f"{removed_assistant['role']}: {removed_assistant['content']}")
            print(f"Context truncated. Removed oldest turn. New token count: {total_tokens}")


        return updated_context

    def summarize_context(self, context: list) -> str:
        """
        Provides a basic summary of the context (can be improved).
        """
        if not context:
            return "The conversation has not started yet."
        # Simple summary for now
        return f"The conversation has {len(context)} turns. The last user message was: '{context[-2]['content']}'"


    def _count_tokens(self, text: str) -> int:
        """Counts tokens using the loaded tokenizer."""
        return len(self.tokenizer.encode(text))

class LLMError(Exception):
    """Custom exception for LLM related errors."""
    pass