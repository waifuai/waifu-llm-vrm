# src/pywaifu/vrm.py
from .character import Character
from .godot import GodotConnector

class VRMCharacter(Character):
    """Represents a VRoid character, extending the Character class."""

    def __init__(self, name: str, personality: str, model: str = None, godot_connector: GodotConnector = None, vrm_node_path: str = None):
        """
        Initializes the VRM character.
        """
        super().__init__(name, personality, model, godot_connector)
        self.vrm_node_path = vrm_node_path

    def play_animation(self, animation_name: str, blend_time: float = 0.0) -> None:
        """Plays a VRM animation in Godot."""
        if self.godot_connector:
            self.godot_connector.rpc("play_animation", self.vrm_node_path, animation_name, blend_time)

    def set_expression(self, expression_name: str, value: float) -> None:
        """Sets a VRM blend shape value in Godot."""
        if self.godot_connector:
          self.godot_connector.rpc("set_expression", self.vrm_node_path, expression_name, value)

    def get_animation_list(self) -> list:
        """Gets animation list."""
        #Need to be called from godot.
        if self.godot_connector:
            return self.godot_connector.rpc("get_animation_list", self.vrm_node_path)
        return []

    def get_blendshape_list(self) -> list:
        """Gets blendshape list"""
        #Need to be called from godot.
        if self.godot_connector:
            return self.godot_connector.rpc("get_blendshape_list", self.vrm_node_path)
        return []