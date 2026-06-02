#config/settings.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class ModelConfig:
    api_key: str
    base_url: str
    model_name: str
    output_dir: str

class Settings:
    MODELS_CONFIG: Dict[str, ModelConfig] = {
        "qwen": ModelConfig(
            api_key="your_api_key",  # 替换为实际API Key
            base_url="https://openrouter.ai/api/v1",
            model_name="qwen/qwen3-8b",
            output_dir=r""
        )
    }



settings = Settings()
