import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "settings", "ukranian_weekname.json")


class JSONLoader:
    def __init__(self, config_path=CONFIG_PATH):
        with open(config_path, 'r') as f:
            self._config = json.load(f)

    def __getattr__(self, name):
        return self._config.get(name)
