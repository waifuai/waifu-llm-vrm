"""
Utility functions for pywaifu.

This module provides utility functions and custom exceptions used throughout the pywaifu library.
It includes API key management, data serialization, and custom error handling.

Functions:
    load_gemini_api_key(): Loads the Google Gemini API key from the user's home directory
    serialize_data(data): Converts dictionary data to JSON string
    deserialize_data(data_str): Converts JSON string back to dictionary

Exceptions:
    ApiKeyNotFoundError: Raised when the Google Gemini API key file is missing or invalid

The API key should be stored in ~/.api-gemini file in the user's home directory.
This file should contain only the API key without any additional formatting.
"""
import os
import json # Keep json for existing serialize/deserialize functions

class ApiKeyNotFoundError(Exception):
    """Custom exception for when the API key file is missing or empty."""
    pass

def load_gemini_api_key() -> str:
    """
    Loads the Google Gemini API key from the ~/.api-gemini file.

    Returns:
        The API key as a string.

    Raises:
        ApiKeyNotFoundError: If the file ~/.api-gemini does not exist,
                             is empty, or cannot be read.
    """
    api_key_path = os.path.expanduser("~/.api-gemini")
    try:
        if not os.path.exists(api_key_path):
            raise ApiKeyNotFoundError(
                f"API key file not found at: {api_key_path}. "
                "Please create this file and place your Google Gemini API key inside."
            )

        with open(api_key_path, 'r') as f:
            api_key = f.read().strip()

        if not api_key:
            raise ApiKeyNotFoundError(
                f"API key file at {api_key_path} is empty. "
                "Please ensure your Google Gemini API key is present in the file."
            )
        return api_key
    except Exception as e:
        # Catch potential permission errors or other file reading issues
        raise ApiKeyNotFoundError(
            f"Failed to load API key from {api_key_path}: {e}"
        ) from e

# Keep existing utility functions if they are still needed elsewhere
# (Currently serialize/deserialize are not used by the core refactored logic,
# but might be used by Godot communication or other parts)
def serialize_data(data: dict) -> str:
  """Serializes to json."""
  return json.dumps(data)

def deserialize_data(data_str: str) -> dict:
  """Deserializes from json."""
  return json.loads(data_str)