import json
import warnings
import glob
import os

warnings.filterwarnings("ignore")
from config.settings import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def load_jsonl(path):
    all_data = []
    try:
        if os.path.isdir(path):
            jsonl_files = glob.glob(os.path.join(path, "*.jsonl"))
            if not jsonl_files:
                print(f"警告: 目录 {path} 下未找到.jsonl文件")
                return []
            print(f"找到 {len(jsonl_files)} 个jsonl文件，开始加载...")
        else:
            jsonl_files = [path]

        for file_path in jsonl_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = [json.loads(line) for line in f if line.strip()]
                all_data.extend(file_data)
        print(f"\n数据加载完成，共 {len(all_data)} 条样本")
        return all_data
    except Exception as e:
        print(f"数据加载错误: {e}")
        return []


def preprocess(ex, tokenizer, max_len):
    history_blocks = ex.get("history_context", "")
    current_block = ex.get("current_block", "")
    label = ex.get("label", {})

    input_text = SYSTEM_PROMPT + USER_PROMPT_TEMPLATE.format(
        history_blocks=history_blocks,
        current_block=current_block
    )

    # 增加容错处理，防止缺失字段导致崩溃
    output_dict = {
        "CoT": str(label.get("CoT", "")),
        "L_f": float(label.get("L_f", 0.5)),
        "L_n": float(label.get("L_n", 0.5)),
        "L_t": float(label.get("L_t", 0.5)),
        "L_s": float(label.get("L_s", 0.5))
    }

    output_text = json.dumps(output_dict, ensure_ascii=False)
    full_text = input_text + output_text

    full_tokens = tokenizer(
        full_text,
        truncation=True,
        max_length=max_len,
        padding=False,
        add_special_tokens=True,
        return_tensors=None
    )

    input_tokens = tokenizer(
        input_text,
        add_special_tokens=True,
        return_tensors=None
    )
    input_len = len(input_tokens["input_ids"])

    labels = full_tokens["input_ids"].copy()
    labels[:input_len] = [-100] * input_len

    return {
        "input_ids": full_tokens["input_ids"],
        "attention_mask": full_tokens.get("attention_mask", [1] * len(full_tokens["input_ids"])),
        "labels": labels
    }
