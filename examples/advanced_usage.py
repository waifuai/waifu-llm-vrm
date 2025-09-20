"""
Advanced usage example for pywaifu.

This script demonstrates advanced features including:
- Custom character behavior
- State management
- VRM integration with dynamic expressions
- Error handling and recovery
- Conversation logging

Usage:
    1. Set up your Google Gemini API key in ~/.api-gemini
    2. Update GODOT_PROJECT_PATH to point to your Godot project directory
    3. Run: python examples/advanced_usage.py
"""

import time
import json
from datetime import datetime
from pywaifu.godot import GodotConnector, GodotError
from pywaifu.character import Character, LLMError
from pywaifu.vrm import VRMCharacter


class CustomCharacter(Character):
    """Extended character with custom behavior and state tracking."""

    def __init__(self, name, personality, **kwargs):
        super().__init__(name, personality, **kwargs)
        self.interaction_count = 0
        self.mood = "neutral"
        self.topics_discussed = set()
        self.conversation_log = []
        self.last_interaction_time = None

    def talk(self, input_text):
        """Override talk method to add custom behavior."""
        self.interaction_count += 1
        self.last_interaction_time = datetime.now()

        # Extract topics from user input
        topics = self._extract_topics(input_text)
        self.topics_discussed.update(topics)

        # Adjust mood based on input
        self._update_mood(input_text)

        # Get response from parent class
        response = super().talk(input_text)

        # Log conversation
        log_entry = {
            "timestamp": self.last_interaction_time.isoformat(),
            "user_input": input_text,
            "character_response": response,
            "mood": self.mood,
            "topics": list(topics)
        }
        self.conversation_log.append(log_entry)

        # Add personality-based responses
        if self.interaction_count % 5 == 0:
            response += f" (This is our {self.interaction_count}th conversation! I love chatting with you!)"

        if "sad" in self.mood:
            response += " (I'm feeling a bit down, but talking with you helps!)"

        return response

    def _extract_topics(self, text):
        """Simple topic extraction from user input."""
        topics = set()
        topic_keywords = {
            "technology": ["computer", "software", "programming", "tech", "ai", "robot"],
            "gaming": ["game", "play", "gaming", "video games", "console"],
            "music": ["music", "song", "band", "artist", "concert"],
            "movies": ["movie", "film", "cinema", "actor", "director"],
            "food": ["food", "eat", "drink", "restaurant", "recipe"],
            "travel": ["travel", "trip", "vacation", "country", "city"]
        }

        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.add(topic)

        return topics

    def _update_mood(self, text):
        """Update character mood based on user input."""
        text_lower = text.lower()

        positive_words = ["happy", "great", "awesome", "love", "wonderful", "excited", "amazing"]
        negative_words = ["sad", "angry", "upset", "disappointed", "terrible", "awful", "hate"]

        if any(word in text_lower for word in positive_words):
            self.mood = "happy"
        elif any(word in text_lower for word in negative_words):
            self.mood = "sad"
        else:
            self.mood = "neutral"

    def get_stats(self):
        """Get character statistics."""
        return {
            "name": self.name,
            "interaction_count": self.interaction_count,
            "current_mood": self.mood,
            "topics_discussed": list(self.topics_discussed),
            "total_conversations": len(self.conversation_log)
        }

    def save_conversation_log(self, filename="conversation_log.json"):
        """Save conversation log to file."""
        with open(filename, 'w') as f:
            json.dump(self.conversation_log, f, indent=2)
        print(f"Conversation log saved to {filename}")


def main():
    # Configuration
    GODOT_PROJECT_PATH = "path/to/your/godot_project"
    CHARACTER_NAME = "Yui"
    CHARACTER_PERSONALITY = (
        "Kind, helpful, and intelligent AI assistant. "
        "Enjoys talking about technology and gaming. "
        "Has a cheerful personality and loves making friends."
    )
    VRM_NODE_PATH = "/root/Scene/VRMNode"
    USE_VRM = False  # Set to True for VRM functionality

    connector = None
    character = None

    try:
        print("=== Advanced pywaifu Example ===")
        print("This example shows custom character behavior and state tracking.")
        print("Ensure your Google Gemini API key is stored in ~/.api-gemini")
        print()

        # Initialize Godot connection
        print("Initializing Godot Connector...")
        connector = GodotConnector(GODOT_PROJECT_PATH)
        connector.connect()
        print("Connector ready.")
        print()

        # Create character
        print(f"Creating advanced character: {CHARACTER_NAME}...")
        if USE_VRM:
            character = VRMCharacter(
                name=CHARACTER_NAME,
                personality=CHARACTER_PERSONALITY,
                godot_connector=connector,
                vrm_node_path=VRM_NODE_PATH
            )
            print("VRM Character created with advanced features.")
        else:
            character = CustomCharacter(
                name=CHARACTER_NAME,
                personality=CHARACTER_PERSONALITY,
                godot_connector=connector
            )
            print("Custom Character created with advanced features.")
        print()

        # Display character info
        stats = character.get_stats()
        print("Character Stats:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()

        print("=== Starting Advanced Conversation ===")
        print("Commands:")
        print("  'stats' - Show character statistics")
        print("  'save' - Save conversation log")
        print("  'quit' or 'exit' - End conversation")
        print()

        while True:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break

            elif user_input.lower() == "stats":
                stats = character.get_stats()
                print(f"\n{character.name}'s Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print()

            elif user_input.lower() == "save":
                character.save_conversation_log()
                print("Conversation log saved.")
                print()

            else:
                print(f"{character.name}: ...thinking...")
                try:
                    response = character.talk(user_input)
                    print(f"{character.name}: {response}")

                    # VRM-specific actions
                    if USE_VRM and isinstance(character, VRMCharacter):
                        if "wave" in user_input.lower():
                            print(f"[{character.name} performs wave animation]")
                            character.play_animation("Wave")
                            character.set_expression("Happy", 0.8)
                        elif character.mood == "happy":
                            character.play_animation("Excited")
                            character.set_expression("Joy", 0.7)
                        elif character.mood == "sad":
                            character.play_animation("Sad")
                            character.set_expression("Sad", 0.6)
                        else:
                            character.play_animation("Idle")
                            character.set_expression("Neutral", 1.0)

                    print()

                except LLMError as e:
                    print(f"LLM Error: {e}")
                    print("Continuing conversation...")
                    print()
                except Exception as e:
                    print(f"Unexpected error during conversation: {e}")
                    print("Continuing conversation...")
                    print()

    except GodotError as e:
        print(f"Failed to connect to Godot: {e}")
        print("You can still chat with the character, but VRM features won't work.")
        print()

        # Continue without Godot
        character = CustomCharacter(
            name=CHARACTER_NAME,
            personality=CHARACTER_PERSONALITY
        )

        print("=== Starting Conversation (No Godot) ===")
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit"]:
                break

            try:
                response = character.talk(user_input)
                print(f"{character.name}: {response}")
                print()
            except LLMError as e:
                print(f"LLM Error: {e}")
                print()

    except LLMError as e:
        print(f"Failed to initialize character: {e}")
    except KeyboardInterrupt:
        print("\nUser interrupted. Exiting...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        if character:
            print(f"\nFinal statistics for {character.name}:")
            stats = character.get_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")

            # Save final conversation log
            try:
                character.save_conversation_log()
            except Exception:
                pass

        if connector:
            print("Disconnecting from Godot...")
            connector.disconnect()

        print("Thank you for chatting! Goodbye!")


if __name__ == "__main__":
    main()