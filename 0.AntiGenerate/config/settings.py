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
    base_dataset_path=''

   #deepseek-v3(fast-thinking)
   #判断是否为诈骗
   #Determine if it is a scam
    MODELS_CONFIG: Dict[str, ModelConfig] = {
        "DeepSeekv3": ModelConfig(
            api_key="your_api_key",
            base_url="https://api.deepseek.com/v1",
            model_name="deepseek-chat",
            prompt_template='''''',
            max_tokens = 8192
        ),

        #GPT Gemini DouBao
        #生成对话
        #Generate a dialogue
        "Gemini": ModelConfig(
            api_key="your_api_key",
            base_url="https://openrouter.ai/api/v1",
            model_name="model_name",
            prompt_template='''''',
            max_tokens = 32*1024
        ),
    }



settings =Settings()


#系统配置
SYSTEM_CONFIG = {
    'max_attempts': 5,
    'output_dir': r"",
    'csv_path': r"xxxx/“杀猪盘” 诈骗(200).csv"
    #诈骗新闻报道背景
    #Background of fraud news reports
}

