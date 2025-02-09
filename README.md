# pywaifu

A Python library for creating AI waifus in Godot using VRM models.

## Usage

```python
from pywaifu.godot import GodotConnector
from pywaifu.character import Character

connector = GodotConnector("path/to/your/godot_project")
connector.connect()

yui = Character(
    name="Yui",
    personality="Kind, helpful, and a little clumsy.",
    godot_connector=connector
)

print(yui.talk("Hello"))

connector.disconnect()