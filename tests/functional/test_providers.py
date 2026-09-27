"""
Functional tests for VADER LLM provider integrations.
Tests provider health checks, model listing, and generation capabilities.
"""
import pytest
from vader.providers.mock import MockProvider
from vader.providers.base import BaseProvider, ModelInfo
from vader.providers.manager import ProviderManager


class TestMockProvider:
    """Test MockProvider functionality for orchestration testing."""

    def test_mock_provider_health_check(self):
        """Test that mock provider health check always returns True."""
        provider = MockProvider()
        assert provider.health_check() is True

    def test_mock_provider_list_models(self):
        """Test that mock provider returns model list."""
        provider = MockProvider()
        models = provider.list_models()

        assert isinstance(models, list)
        assert len(models) > 0
        assert isinstance(models[0], ModelInfo)
        assert models[0].id == "vader-mock-planner"
        assert models[0].name == "Vader Instant Test Model"

    def test_mock_provider_generate_architect_response(self):
        """Test architect agent response generation."""
        provider = MockProvider()
        prompt = "Create an architectural execution plan for a todo app"
        system_prompt = "Vader Architect Agent"

        response = provider.generate(prompt, system_prompt=system_prompt)

        assert isinstance(response, str)
        assert "PLAN:" in response
        assert "CRITICAL_FILES:" in response
        assert "VERIFICATION_STEPS:" in response

    def test_mock_provider_generate_coder_response(self):
        """Test coder agent response with file blocks."""
        provider = MockProvider()
        prompt = "Implement all requested changes with complete files"
        system_prompt = "Vader Coder Agent"

        response = provider.generate(prompt, system_prompt=system_prompt)

        assert isinstance(response, str)
        assert "FILE:" in response
        assert "```" in response
        # Should contain HTML, CSS, and JS files
        assert "index.html" in response
        assert "style.css" in response
        assert "app.js" in response

    def test_mock_provider_generate_reviewer_response(self):
        """Test reviewer agent safety validation."""
        provider = MockProvider()
        prompt = "Review the final diffs for security issues"
        system_prompt = "Reviewer Agent"

        response = provider.generate(prompt, system_prompt=system_prompt)

        assert isinstance(response, str)
        assert "STATUS:" in response
        assert any(keyword in response for keyword in ["APPROVED", "REASONING"])

    def test_mock_provider_stream(self):
        """Test streaming response generation."""
        provider = MockProvider()
        prompt = "Test streaming"

        stream = provider.stream(prompt)
        chunks = list(stream)

        assert len(chunks) > 0
        assert isinstance(chunks[0], str)

    def test_mock_provider_model_attribute(self):
        """Test that mock provider has model attribute."""
        provider = MockProvider(model_name="custom-model")
        assert provider.model == "custom-model"

        provider_default = MockProvider()
        assert provider_default.model == "vader-mock-planner"


class TestProviderManager:
    """Test ProviderManager for provider instantiation and switching."""

    def test_get_mock_provider(self):
        """Test retrieving mock provider from manager."""
        provider = ProviderManager.get_provider(provider_name="mock")

        assert isinstance(provider, MockProvider)
        assert provider.health_check() is True

    def test_get_provider_with_model(self):
        """Test retrieving provider with custom model."""
        provider = ProviderManager.get_provider(
            provider_name="mock",
            model_name="test-model"
        )

        assert isinstance(provider, MockProvider)
        assert provider.model == "test-model"

    def test_provider_interface_compliance(self):
        """Test that mock provider implements BaseProvider interface."""
        provider = MockProvider()

        # Check all abstract methods are implemented
        assert hasattr(provider, 'health_check')
        assert hasattr(provider, 'list_models')
        assert hasattr(provider, 'generate')
        assert hasattr(provider, 'stream')

        # Verify they're callable
        assert callable(provider.health_check)
        assert callable(provider.list_models)
        assert callable(provider.generate)
        assert callable(provider.stream)


class TestProviderGeneration:
    """Test provider generation with various inputs."""

    def test_empty_prompt_generation(self):
        """Test generation with empty prompt."""
        provider = MockProvider()
        response = provider.generate("")

        assert isinstance(response, str)
        assert len(response) > 0

    def test_long_prompt_generation(self):
        """Test generation with long context prompt."""
        provider = MockProvider()
        long_prompt = "Generate code " * 1000  # Long prompt

        response = provider.generate(long_prompt)
        assert isinstance(response, str)

    def test_special_characters_in_prompt(self):
        """Test generation with special characters."""
        provider = MockProvider()
        prompt = "Generate code with symbols: @#$%^&*(){}[]|\\/<>?~`"

        response = provider.generate(prompt)
        assert isinstance(response, str)

    def test_multiline_system_prompt(self):
        """Test generation with multiline system prompt."""
        provider = MockProvider()
        system_prompt = """You are an architect.
        You create plans.
        You design systems."""

        response = provider.generate("Create a plan", system_prompt=system_prompt)
        assert isinstance(response, str)
