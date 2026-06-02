#config/settings.py
from dataclasses import dataclass
@dataclass
class ModelConfig:
    api_key: str
    base_url: str
    model_name: str
    prompt_template: str
    max_tokens: int



#API配置
from typing import Dict
class Settings:
    MODELS_CONFIG: Dict[str, ModelConfig] = {
        "reasoner": ModelConfig(
            api_key="your-api-key",
            base_url="https://api.deepseek.com",
            model_name="deepseek-reasoner",
            prompt_template='''''',
            max_tokens = 40000
        )
    }

settings =Settings()


