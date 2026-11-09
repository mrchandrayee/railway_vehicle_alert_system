import yaml

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def parse_source(value):
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return value
