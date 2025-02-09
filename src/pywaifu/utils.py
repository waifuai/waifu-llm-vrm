# src/pywaifu/utils.py
import json

def serialize_data(data: dict) -> str:
  """Serializes to json."""
  return json.dumps(data)

def deserialize_data(data_str: str) -> dict:
  """Deserializes from json."""
  return json.loads(data_str)