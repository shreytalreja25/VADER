from abc import ABC, abstractmethod
from typing import Generator, List, Dict, Any, Optional
from pydantic import BaseModel

class ModelInfo(BaseModel):
    id: str
    name: str
    size_bytes: Optional[int] = None
    quantization: Optional[str] = None
    family: Optional[str] = None
    parameters: Optional[str] = None

class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_generated: Optional[int] = 0
    done: bool = True

class BaseProvider(ABC):
    @abstractmethod
    def health_check(self) -> bool:
        pass

    @abstractmethod
    def list_models(self) -> List[ModelInfo]:
        pass

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "", stream: bool = False) -> str:
        pass

    @abstractmethod
    def stream(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        pass
