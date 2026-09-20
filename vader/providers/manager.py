from typing import Optional
from vader.providers.base import BaseProvider
from vader.providers.ollama import OllamaProvider
from vader.providers.quantized import QuantizedProvider
from vader.providers.cloud import CloudProvider
from vader.config import config_manager

class ProviderManager:
    @staticmethod
    def get_provider(
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> BaseProvider:
        p_name = (provider_name or config_manager.get("provider", "ollama")).lower()
        active_model = model_name or config_manager.get("model", "qwen2.5-coder:7b")

        if p_name == "ollama":
            return OllamaProvider(endpoint=endpoint, default_model=active_model)
        elif p_name in ["quantized", "gguf", "llamacpp"]:
            return QuantizedProvider(endpoint=endpoint, model_name=active_model)
        elif p_name in ["cloud", "anthropic", "openai", "deepseek"]:
            return CloudProvider(provider_type=p_name, model_name=active_model)
        else:
            return OllamaProvider(endpoint=endpoint, default_model=active_model)

provider_manager = ProviderManager()
