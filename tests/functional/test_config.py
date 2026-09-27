"""
Functional tests for VADER configuration management.
Tests config loading, saving, get/set operations, and defaults.
"""
import os
import json
import tempfile
import pytest
from pathlib import Path
from vader.config import ConfigManager, DEFAULT_CONFIG, GLOBAL_CONFIG_FILE


class TestConfigManager:
    """Test configuration manager functionality."""

    def test_config_manager_initialization(self):
        """Test that config manager initializes with defaults."""
        config_mgr = ConfigManager()

        assert config_mgr.config is not None
        assert isinstance(config_mgr.config, dict)
        assert "provider" in config_mgr.config
        assert "model" in config_mgr.config

    def test_default_config_structure(self):
        """Test that default config has expected structure."""
        assert "provider" in DEFAULT_CONFIG
        assert "model" in DEFAULT_CONFIG
        assert "ollama" in DEFAULT_CONFIG
        assert "quantized" in DEFAULT_CONFIG
        assert "cloud" in DEFAULT_CONFIG
        assert "orchestration" in DEFAULT_CONFIG
        assert "guardrails" in DEFAULT_CONFIG

    def test_default_config_values(self):
        """Test default configuration values."""
        assert DEFAULT_CONFIG["provider"] == "ollama"
        assert "qwen" in DEFAULT_CONFIG["model"]
        assert DEFAULT_CONFIG["temperature"] == 0.2
        assert DEFAULT_CONFIG["max_tokens"] == 4096

    def test_ollama_default_config(self):
        """Test Ollama provider default configuration."""
        ollama_config = DEFAULT_CONFIG["ollama"]

        assert "endpoint" in ollama_config
        assert "localhost:11434" in ollama_config["endpoint"]
        assert ollama_config["timeout_seconds"] == 120

    def test_orchestration_default_config(self):
        """Test orchestration default configuration."""
        orch_config = DEFAULT_CONFIG["orchestration"]

        assert orch_config["max_repair_iterations"] == 3
        assert orch_config["auto_lint"] is True
        assert orch_config["auto_test"] is True
        assert orch_config["sandbox_timeout"] == 60

    def test_guardrails_protected_paths(self):
        """Test guardrails protected paths configuration."""
        guardrails = DEFAULT_CONFIG["guardrails"]

        assert ".git" in guardrails["protected_paths"]
        assert ".env" in guardrails["protected_paths"]
        assert "node_modules" in guardrails["protected_paths"]
        assert guardrails["require_confirmation_for_deletions"] is True


class TestConfigGetOperations:
    """Test config get operations."""

    def test_get_top_level_key(self):
        """Test getting top-level configuration key."""
        config_mgr = ConfigManager()

        provider = config_mgr.get("provider")
        assert provider is not None
        assert isinstance(provider, str)

    def test_get_nested_key(self):
        """Test getting nested configuration key."""
        config_mgr = ConfigManager()

        endpoint = config_mgr.get("ollama.endpoint")
        assert endpoint is not None
        assert "localhost" in endpoint

    def test_get_deeply_nested_key(self):
        """Test getting deeply nested configuration key."""
        config_mgr = ConfigManager()

        protected_paths = config_mgr.get("guardrails.protected_paths")
        assert protected_paths is not None
        assert isinstance(protected_paths, list)
        assert len(protected_paths) > 0

    def test_get_nonexistent_key_with_default(self):
        """Test getting nonexistent key returns default value."""
        config_mgr = ConfigManager()

        value = config_mgr.get("nonexistent.key", "default_value")
        assert value == "default_value"

    def test_get_nonexistent_key_without_default(self):
        """Test getting nonexistent key returns None."""
        config_mgr = ConfigManager()

        value = config_mgr.get("nonexistent.key")
        assert value is None

    def test_get_partial_nested_key(self):
        """Test getting partial nested configuration."""
        config_mgr = ConfigManager()

        ollama_config = config_mgr.get("ollama")
        assert ollama_config is not None
        assert isinstance(ollama_config, dict)
        assert "endpoint" in ollama_config


class TestConfigSetOperations:
    """Test config set operations."""

    def test_set_top_level_key(self):
        """Test setting top-level configuration key."""
        config_mgr = ConfigManager()

        config_mgr.set("provider", "mock", persist=False)
        assert config_mgr.get("provider") == "mock"

    def test_set_nested_key(self):
        """Test setting nested configuration key."""
        config_mgr = ConfigManager()

        config_mgr.set("ollama.endpoint", "http://custom:11434", persist=False)
        assert config_mgr.get("ollama.endpoint") == "http://custom:11434"

    def test_set_deeply_nested_key(self):
        """Test setting deeply nested configuration key."""
        config_mgr = ConfigManager()

        config_mgr.set("orchestration.max_repair_iterations", 5, persist=False)
        assert config_mgr.get("orchestration.max_repair_iterations") == 5

    def test_set_creates_nested_structure(self):
        """Test that set creates nested structure if missing."""
        config_mgr = ConfigManager()

        config_mgr.set("new.nested.key", "value", persist=False)
        assert config_mgr.get("new.nested.key") == "value"

    def test_set_overwrites_existing_value(self):
        """Test that set overwrites existing values."""
        config_mgr = ConfigManager()

        original = config_mgr.get("temperature")
        config_mgr.set("temperature", 0.7, persist=False)
        assert config_mgr.get("temperature") == 0.7
        assert config_mgr.get("temperature") != original

    def test_set_different_types(self):
        """Test setting values of different types."""
        config_mgr = ConfigManager()

        # String
        config_mgr.set("test.string", "value", persist=False)
        assert config_mgr.get("test.string") == "value"

        # Integer
        config_mgr.set("test.int", 42, persist=False)
        assert config_mgr.get("test.int") == 42

        # Boolean
        config_mgr.set("test.bool", True, persist=False)
        assert config_mgr.get("test.bool") is True

        # List
        config_mgr.set("test.list", [1, 2, 3], persist=False)
        assert config_mgr.get("test.list") == [1, 2, 3]

        # Dict
        config_mgr.set("test.dict", {"key": "value"}, persist=False)
        assert config_mgr.get("test.dict") == {"key": "value"}


class TestConfigPersistence:
    """Test configuration persistence to disk."""

    def test_save_global_config(self, tmp_path, monkeypatch):
        """Test saving global configuration to file."""
        # Create temporary config directory
        temp_config_dir = tmp_path / ".vader"
        temp_config_file = temp_config_dir / "config.json"
        temp_config_dir.mkdir(parents=True, exist_ok=True)

        # Monkeypatch the global config file location
        monkeypatch.setattr("vader.config.GLOBAL_CONFIG_FILE", temp_config_file)
        monkeypatch.setattr("vader.config.GLOBAL_CONFIG_DIR", temp_config_dir)

        config_mgr = ConfigManager()
        config_mgr.set("provider", "test_provider", persist=False)
        config_mgr.save_global()

        assert temp_config_file.exists()

        # Verify saved content
        with open(temp_config_file, "r") as f:
            saved_config = json.load(f)

        assert saved_config["provider"] == "test_provider"

    def test_load_existing_config(self, tmp_path, monkeypatch):
        """Test loading existing configuration from file."""
        # Create temporary config with custom values
        temp_config_dir = tmp_path / ".vader"
        temp_config_file = temp_config_dir / "config.json"
        temp_config_dir.mkdir(parents=True, exist_ok=True)

        custom_config = {
            "provider": "custom_provider",
            "model": "custom_model",
            "temperature": 0.9
        }

        with open(temp_config_file, "w") as f:
            json.dump(custom_config, f)

        # Monkeypatch config paths
        monkeypatch.setattr("vader.config.GLOBAL_CONFIG_FILE", temp_config_file)
        monkeypatch.setattr("vader.config.GLOBAL_CONFIG_DIR", temp_config_dir)

        # Load config
        config_mgr = ConfigManager()

        assert config_mgr.get("provider") == "custom_provider"
        assert config_mgr.get("model") == "custom_model"
        assert config_mgr.get("temperature") == 0.9

    def test_config_merge_with_defaults(self, tmp_path, monkeypatch):
        """Test that user config merges with defaults."""
        temp_config_dir = tmp_path / ".vader"
        temp_config_file = temp_config_dir / "config.json"
        temp_config_dir.mkdir(parents=True, exist_ok=True)

        # Only override one value
        partial_config = {"provider": "custom_provider"}

        with open(temp_config_file, "w") as f:
            json.dump(partial_config, f)

        monkeypatch.setattr("vader.config.GLOBAL_CONFIG_FILE", temp_config_file)
        monkeypatch.setattr("vader.config.GLOBAL_CONFIG_DIR", temp_config_dir)

        config_mgr = ConfigManager()

        # Custom value should be loaded
        assert config_mgr.get("provider") == "custom_provider"

        # Default values should still exist
        assert config_mgr.get("temperature") == 0.2
        assert config_mgr.get("ollama.endpoint") is not None
