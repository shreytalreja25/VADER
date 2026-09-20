import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

GLOBAL_CONFIG_DIR = Path.home() / ".vader"
GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / "config.json"
LOCAL_CONFIG_FILE = Path(".vader") / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "provider": "ollama",
    "model": "qwen2.5-coder:7b",
    "temperature": 0.2,
    "max_tokens": 4096,
    "ollama": {
        "endpoint": "http://localhost:11434",
        "timeout_seconds": 120,
    },
    "quantized": {
        "endpoint": "http://localhost:8080/v1",
        "format": "gguf",
        "quant_preset": "Q4_K_M",
        "context_window": 16384,
        "models_dir": str(Path.home() / ".vader" / "models"),
    },
    "cloud": {
        "anthropic_api_key": "",
        "openai_api_key": "",
        "deepseek_api_key": "",
        "openrouter_api_key": "",
    },
    "orchestration": {
        "max_repair_iterations": 3,
        "auto_lint": True,
        "auto_test": True,
        "sandbox_timeout": 60,
    },
    "guardrails": {
        "protected_paths": [
            ".git",
            ".env",
            "node_modules",
            "venv",
            ".venv",
            "package-lock.json",
            "poetry.lock"
        ],
        "require_confirmation_for_deletions": True
    }
}

class ConfigManager:
    def __init__(self):
        GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        cfg = DEFAULT_CONFIG.copy()
        if GLOBAL_CONFIG_FILE.exists():
            try:
                with open(GLOBAL_CONFIG_FILE, "r", encoding="utf-8") as f:
                    user_cfg = json.load(f)
                    self._deep_update(cfg, user_cfg)
            except Exception:
                pass
        
        if LOCAL_CONFIG_FILE.exists():
            try:
                with open(LOCAL_CONFIG_FILE, "r", encoding="utf-8") as f:
                    local_cfg = json.load(f)
                    self._deep_update(cfg, local_cfg)
            except Exception:
                pass
        return cfg

    def _deep_update(self, base: Dict[str, Any], update: Dict[str, Any]):
        for k, v in update.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                self._deep_update(base[k], v)
            else:
                base[k] = v

    def save_global(self, new_config: Optional[Dict[str, Any]] = None):
        if new_config:
            self.config = new_config
        GLOBAL_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(GLOBAL_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def save_local(self):
        LOCAL_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOCAL_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        parts = key.split(".")
        val = self.config
        for p in parts:
            if isinstance(val, dict) and p in val:
                val = val[p]
            else:
                return default
        return val

    def set(self, key: str, value: Any, persist: bool = True):
        parts = key.split(".")
        d = self.config
        for p in parts[:-1]:
            if p not in d or not isinstance(d[p], dict):
                d[p] = {}
            d = d[p]
        d[parts[-1]] = value
        if persist:
            self.save_global()

config_manager = ConfigManager()
