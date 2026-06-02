#utils/dialogue_parser.py
import json
from typing import List, Dict

def parse_dialogue_jsonl(file_path: str) -> List[Dict]:
    """解析jsonl文件，返回对话列表（每行一个JSON对象）"""
    dialogues = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                dialogues.append(json.loads(line))
    return dialogues