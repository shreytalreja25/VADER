import os
import json
from pathlib import Path
from typing import Generator, List, Optional, Dict, Any
import httpx
from vader.providers.base import BaseProvider, ModelInfo
from vader.config import config_manager

class QuantizedProvider(BaseProvider):
    """
    Plug-and-play local quantized model provider.
    Connects to local OpenAI-compatible inference backends (llama.cpp server, vLLM, Tabby, or Ollama)
    and manages local .gguf / quantized model files.
    """
    def __init__(self, endpoint: Optional[str] = None, model_name: Optional[str] = None):
        self.endpoint = (endpoint or config_manager.get("quantized.endpoint", "http://localhost:8080/v1")).rstrip("/")
        self.model = model_name or config_manager.get("model", "qwen2.5-coder-7b-instruct-q4_k_m")
        self.models_dir = Path(config_manager.get("quantized.models_dir", Path.home() / ".vader" / "models"))
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.endpoint}/models")
                return res.status_code == 200
        except Exception:
            return False

    def list_local_gguf_files(self) -> List[Dict[str, Any]]:
        files = []
        if self.models_dir.exists():
            for f in self.models_dir.glob("*.gguf"):
                size_gb = round(f.stat().st_size / (1024 ** 3), 2)
                quant = "Q4_K_M" if "q4" in f.name.lower() else ("Q8_0" if "q8" in f.name.lower() else "GGUF")
                files.append({
                    "name": f.name,
                    "path": str(f.resolve()),
                    "size_gb": size_gb,
                    "quantization": quant,
                    "recommended_vram_gb": round(size_gb * 1.2, 1)
                })
        return files

    def list_models(self) -> List[ModelInfo]:
        models = []
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.endpoint}/models")
                if res.status_code == 200:
                    data = res.json()
                    for m in data.get("data", []):
                        mid = m.get("id", "")
                        models.append(ModelInfo(
                            id=mid,
                            name=mid,
                            family="GGUF / Quantized",
                            quantization=config_manager.get("quantized.quant_preset", "Q4_K_M")
                        ))
        except Exception:
            pass

        # Also add local files found in models directory
        for gf in self.list_local_gguf_files():
            if not any(m.id == gf["name"] for m in models):
                models.append(ModelInfo(
                    id=gf["name"],
                    name=f"{gf['name']} ({gf['size_gb']} GB)",
                    family="Local GGUF",
                    quantization=gf["quantization"]
                ))
        return models

    def generate(self, prompt: str, system_prompt: str = "", stream: bool = False) -> str:
        if stream:
            return "".join(list(self.stream(prompt, system_prompt)))

        url = f"{self.endpoint}/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": config_manager.get("temperature", 0.2),
            "max_tokens": config_manager.get("max_tokens", 4096),
            "stream": False
        }
        with httpx.Client(timeout=120.0) as client:
            res = client.post(url, json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"Quantized inference error ({res.status_code}): {res.text}")
            data = res.json()
            return data["choices"][0]["message"]["content"]

    def stream(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        url = f"{self.endpoint}/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": config_manager.get("temperature", 0.2),
            "max_tokens": config_manager.get("max_tokens", 4096),
            "stream": True
        }
        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", url, json=payload) as response:
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
