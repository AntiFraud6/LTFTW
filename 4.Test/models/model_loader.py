import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import config.settings as cfg
from peft import PeftModel

def load_model():
    model_name = cfg.MODEL_NAME
    checkpoint = cfg.CHECKPOINT_PATH if cfg.CHECKPOINT_PATH else None

    print(f"正在加载模型: {model_name}")

    # 加载tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    # 加载基础模型
    # 修改：移除 device_map="auto"
    base_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        # device_map="auto",  <-- 删除这行
        trust_remote_code=True
    )

    # 加载CheckPoint
    if checkpoint:
        model = PeftModel.from_pretrained(base_model, checkpoint)
    else:
        model = base_model

    # 直接返回模型和tokenizer
    return model, tokenizer