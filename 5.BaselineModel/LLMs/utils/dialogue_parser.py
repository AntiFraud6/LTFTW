# utils/dialogue_parser.py
import json
from typing import Dict, List

def parse_dialogue_jsonl(file_path: str) -> List[Dict]:
    dialogues = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line.strip())
                dialogue = {
                    "round_number": data.get("round_number", 0),
                    "dialogue": data.get("dialogue", ""),
                    "is_key": data.get("is_key", "false"),
                    "reason": data.get("reason", "")
                }
                dialogues.append(dialogue)

    dialogues.sort(key=lambda x: x["round_number"])
    return dialogues