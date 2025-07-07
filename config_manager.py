import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".waifu_tagger"
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {"include_rating": False, "exclude_character": False}


class ConfigManager:
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.config.update(json.load(f))
            except Exception as e:
                print(f"[ConfigManager] Failed to load config: {e}")

    def save(self):
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"[ConfigManager] Failed to save config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value
        self.save()

    def get_all(self):
        return self.config.copy()
