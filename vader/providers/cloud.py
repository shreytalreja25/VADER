import os
import json
import httpx
from typing import Generator, List, Optional
from vader.providers.base import BaseProvider, ModelInfo
from vader.config import config_manager

class CloudProvider(BaseProvider):
    """
    Frontier cloud provider fallback (OpenAI, Anthropic, DeepSeek, OpenRouter)
    """
    def __init__(self, provider_type: str = "deepseek", model_name: Optional[str] = None):
        self.provider_type = provider_type
        self.model = model_name or "deepseek-coder"
        self._init_creds()

    def _init_creds(self):
        if self.provider_type == "deepseek":
            self.api_key = os.environ.get("DEEPSEEK_API_KEY", config_manager.get("cloud.deepseek_api_key", ""))
            self.base_url = "https://api.deepseek.com/v1"
        elif self.provider_type == "anthropic":
            self.api_key = os.environ.get("ANTHROPIC_API_KEY", config_manager.get("cloud.anthropic_api_key", ""))
            self.base_url = "https://api.anthropic.com/v1"
        elif self.provider_type == "openai":
            self.api_key = os.environ.get("OPENAI_API_KEY", config_manager.get("cloud.openai_api_key", ""))
            self.base_url = "https://api.openai.com/v1"
        else:
            self.api_key = os.environ.get("OPENROUTER_API_KEY", config_manager.get("cloud.openrouter_api_key", ""))
            self.base_url = "https://openrouter.ai/api/v1"

    def health_check(self) -> bool:
        return bool(self.api_key)

    def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(id="claude-3-7-sonnet", name="Claude 3.7 Sonnet", family="Anthropic"),
            ModelInfo(id="claude-3-5-sonnet", name="Claude 3.5 Sonnet", family="Anthropic"),
            ModelInfo(id="deepseek-coder", name="DeepSeek Coder V2", family="DeepSeek"),
            ModelInfo(id="gpt-4o", name="OpenAI GPT-4o", family="OpenAI"),
        ]

    def generate(self, prompt: str, system_prompt: str = "", stream: bool = False) -> str:
        if stream:
            return "".join(list(self.stream(prompt, system_prompt)))
        
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }
        with httpx.Client(timeout=120.0) as client:
            res = client.post(url, headers=headers, json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"Cloud API error ({res.status_code}): {res.text}")
            return res.json()["choices"][0]["message"]["content"]

    def stream(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "stream": True
        }
        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", url, headers=headers, json=payload) as response:
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        raw = line[6:].strip()
                        if raw == "[DONE]":
                            break
                        try:
                            data = json.loads(raw)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue
