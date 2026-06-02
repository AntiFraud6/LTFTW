#models/model_loader
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config.settings import MODEL_NAME, CHECKPOINT_PATH
from peft import PeftModel
def load_model():
    checkpoint = CHECKPOINT_PATH if CHECKPOINT_PATH else None

    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    torch.cuda.set_device(local_rank)  # 显式设置当前进程的设备

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True
    )

    # 移除 device_map，避免与 DDP 冲突。加载后显式移动到对应 GPU
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        low_cpu_mem_usage=True  # 优化CPU内存占用
    )
    model = model.to(f"cuda:{local_rank}")

    if checkpoint:
        # 修改加载 LoRA 时启用 is_trainable=True
        model = PeftModel.from_pretrained(
            model,
            checkpoint,
            is_trainable=True  # 确保 LoRA 参数可训练
        )
        # 【关键修改】强制将模型切换到训练模式
        model.train()

    return model, tokenizer

