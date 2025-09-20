# src/pywaifu/vrm.py
from .character import Character
from .godot import GodotConnector

class VRMCharacter(Character):
    """Represents a VRoid character, extending the Character class."""

    def __init__(self, name: str, personality: str, godot_connector: GodotConnector = None, vrm_node_path: str = None):
        """
        Initializes the VRM character.
        """
        super().__init__(name, personality, godot_connector)
        self.vrm_node_path = vrm_node_path

    def play_animation(self, animation_name: str, blend_time: float = 0.0) -> None:
        """Plays a VRM animation in Godot."""
        if self.godot_connector:
            try:
                self.godot_connector.rpc("play_animation", self.vrm_node_path, animation_name, blend_time)
            except Exception as e:
                print(f"Warning: Failed to play animation '{animation_name}': {e}")

    def set_expression(self, expression_name: str, value: float) -> None:
        """Sets a VRM blend shape value in Godot."""
        if self.godot_connector:
            try:
                self.godot_connector.rpc("set_expression", self.vrm_node_path, expression_name, value)
            except Exception as e:
                print(f"Warning: Failed to set expression '{expression_name}': {e}")

    def get_animation_list(self) -> list:
        """Gets animation list from Godot."""
        if self.godot_connector:
            try:
                return self.godot_connector.rpc("get_animation_list", self.vrm_node_path)
            except Exception as e:
                print(f"Warning: Failed to get animation list: {e}")
                return []
        return []

    def get_blendshape_list(self) -> list:
        """Gets blendshape list from Godot."""
        if self.godot_connector:
            try:
                return self.godot_connector.rpc("get_blendshape_list", self.vrm_node_path)
            except Exception as e:
                print(f"Warning: Failed to get blendshape list: {e}")
                return []
        return []