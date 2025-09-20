# src/pywaifu/__init__.py
"""
pywaifu - AI-powered characters for Godot game engine.

This package provides classes for creating interactive AI characters
that can be integrated with Godot projects using Google Gemini AI.
"""

__version__ = "1.1.0"

from .character import Character, LLMError
from .vrm import VRMCharacter
from .godot import GodotConnector, GodotError
from .utils import load_gemini_api_key, ApiKeyNotFoundError

__all__ = [
    "Character",
    "VRMCharacter",
    "GodotConnector",
    "LLMError",
    "GodotError",
    "load_gemini_api_key",
    "ApiKeyNotFoundError",
]