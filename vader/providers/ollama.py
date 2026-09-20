import json
import httpx
from typing import Generator, List, Optional, Dict, Any
from vader.providers.base import BaseProvider, ModelInfo
from vader.config import config_manager

class OllamaProvider(BaseProvider):
    def __init__(self, endpoint: Optional[str] = None, default_model: Optional[str] = None):
        self.endpoint = (endpoint or config_manager.get("ollama.endpoint", "http://localhost:11434")).rstrip("/")
        self.model = default_model or config_manager.get("model", "qwen2.5-coder:7b")
        self.timeout = config_manager.get("ollama.timeout_seconds", 120)

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.endpoint}/api/version")
                return res.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[ModelInfo]:
        models = []
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.endpoint}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    for m in data.get("models", []):
                        details = m.get("details", {})
                        models.append(ModelInfo(
                            id=m.get("name", ""),
                            name=m.get("name", ""),
                            size_bytes=m.get("size", 0),
                            quantization=details.get("quantization_level", "Unknown"),
                            family=details.get("family", "Unknown"),
                            parameters=details.get("parameter_size", "Unknown")
                        ))
        except Exception:
            pass
        return models

    def pull_model(self, model_name: str) -> Generator[Dict[str, Any], None, None]:
        url = f"{self.endpoint}/api/pull"
        with httpx.Client(timeout=600.0) as client:
            with client.stream("POST", url, json={"name": model_name}) as response:
                for line in response.iter_lines():
                    if line:
                        try:
                            yield json.loads(line)
                        except Exception:
                            continue

    def generate(self, prompt: str, system_prompt: str = "", stream: bool = False) -> str:
        if stream:
            return "".join(list(self.stream(prompt, system_prompt)))
        
        url = f"{self.endpoint}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": config_manager.get("temperature", 0.2),
                "num_ctx": config_manager.get("max_tokens", 8192)
            }
        }
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(url, json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"Ollama error ({res.status_code}): {res.text}")
            return res.json().get("response", "")

    def stream(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        url = f"{self.endpoint}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "options": {
                "temperature": config_manager.get("temperature", 0.2),
                "num_ctx": config_manager.get("max_tokens", 8192)
            }
        }
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream("POST", url, json=payload) as response:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if chunk:
                                yield chunk
                            if data.get("done", False):
                                break
                        except Exception:
                            continue
