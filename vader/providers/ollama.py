import json
import httpx
from typing import Generator, List, Optional, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn
from vader.providers.base import BaseProvider, ModelInfo
from vader.config import config_manager

console = Console()

class OllamaProvider(BaseProvider):
    def __init__(self, endpoint: Optional[str] = None, default_model: Optional[str] = None):
        self.endpoint = (endpoint or config_manager.get("ollama.endpoint", "http://localhost:11434")).rstrip("/")
        self.model = default_model or config_manager.get("model", "qwen2.5-coder:1.5b")
        self.timeout = config_manager.get("ollama.timeout_seconds", 180)

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

    def pull_model_with_progress(self, model_name: str) -> bool:
        """Pulls a model from Ollama registry with a real-time progress indicator."""
        url = f"{self.endpoint}/api/pull"
        console.print(f"[cyan]Downloading model '[bold]{model_name}[/bold]' from Ollama (~1-2 GB)...[/cyan]")
        try:
            with httpx.Client(timeout=1200.0) as client:
                with client.stream("POST", url, json={"name": model_name}) as response:
                    last_status = ""
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        DownloadColumn(),
                        TransferSpeedColumn(),
                        console=console
                    ) as progress:
                        task_id = progress.add_task(f"Pulling {model_name}", total=100)
                        for line in response.iter_lines():
                            if not line:
                                continue
                            try:
                                data = json.loads(line)
                                status = data.get("status", "")
                                total = data.get("total", 0)
                                completed = data.get("completed", 0)
                                if total > 0:
                                    progress.update(task_id, completed=completed, total=total, description=f"{model_name}: {status}")
                                else:
                                    if status != last_status:
                                        progress.update(task_id, description=f"{model_name}: {status}")
                                        last_status = status
                                if status == "success":
                                    progress.update(task_id, completed=total or 100, total=total or 100, description="[bold green]Download complete![/bold green]")
                                    break
                            except Exception:
                                continue
            console.print(f"[bold green]✔ Successfully pulled {model_name}![/bold green]\n")
            return True
        except Exception as e:
            console.print(f"[bold red]Failed to pull model {model_name}:[/bold red] {e}")
            return False

    def ensure_model_available(self) -> bool:
        """Verifies if the model exists in Ollama; if not, triggers auto-pull."""
        existing = [m.name for m in self.list_models()]
        # Check direct match or without :latest
        if any(self.model in m or m.startswith(self.model) for m in existing):
            return True
        # Model missing, trigger pull
        return self.pull_model_with_progress(self.model)

    def generate(self, prompt: str, system_prompt: str = "", stream: bool = False) -> str:
        if not self.health_check():
            raise ConnectionError(
                f"Cannot connect to Ollama service at {self.endpoint}.\n"
                "Please make sure Ollama is running. Run: 'ollama serve' or launch the Ollama app.\n"
                "Alternatively, test with instant simulator mode: 'vader -p mock'"
            )

        # Check if model exists or auto-pull it
        try:
            return self._execute_generate(prompt, system_prompt, stream=stream)
        except RuntimeError as e:
            err_str = str(e).lower()
            if "not found" in err_str or "404" in err_str:
                console.print(f"[yellow]Model '{self.model}' is not yet downloaded locally.[/yellow]")
                if self.pull_model_with_progress(self.model):
                    return self._execute_generate(prompt, system_prompt, stream=stream)
            raise e

    def _execute_generate(self, prompt: str, system_prompt: str = "", stream: bool = False) -> str:
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
            if res.status_code == 404:
                raise RuntimeError(f"Ollama error (404): model '{self.model}' not found")
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
                if response.status_code == 404:
                    raise RuntimeError(f"Ollama error (404): model '{self.model}' not found")
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
