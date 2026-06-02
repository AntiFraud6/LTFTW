import time
from typing import Dict
import config.settings as cfg
from config.prompt import SYSTEM_PROMPT
from utils.extract_json import extract_json_from_text
from utils.PromptFormat import generate_prompt
import torch


class ModelInferencer:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def infer(self, history: str, current_block: str, block_idx: int, last_block_data: Dict = None) -> Dict:
        prompt = generate_prompt(history, current_block, block_idx, last_block_data)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False
        )

        # 确定设备
        device = self.model.device if hasattr(self.model, 'device') else next(self.model.parameters()).device
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(device)

        generation_kwargs = {
            "max_new_tokens": cfg.MAX_TOKENS,
            "temperature": cfg.TEMPERATURE,
            "do_sample": True,
            "pad_token_id": self.tokenizer.eos_token_id
        }

        for attempt in range(cfg.MAX_RETRIES):
            try:
                with torch.no_grad():
                    # ================= 核心修改开始 =================
                    # 直接使用 self.model，不再需要判断 .module
                    outputs = self.model.generate(
                        **inputs,
                        **generation_kwargs
                    )
                    # ================= 核心修改结束 =================

                generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
                response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

                print('模型原始响应为:')
                print(response)
                result = extract_json_from_text(response)

                if result and all(key in result for key in ['L_f', 'L_n', 'L_t', 'L_s']):
                    round_start = block_idx * 10 - 9
                    round_end = block_idx * 10
                    result['block_range'] = f"{round_start}-{round_end}"
                    return result
                else:
                    print(f"第{attempt + 1}次尝试失败: JSON格式不完整")

                print(result)

            except Exception as e:
                print(f"第{attempt + 1}次尝试失败: {str(e)}")

            if attempt < cfg.MAX_RETRIES - 1:
                time.sleep(1)

        raise ValueError(f"在{cfg.MAX_RETRIES}次尝试后仍无法获得有效JSON响应")
