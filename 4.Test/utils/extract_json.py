# utils/json_utils.py
import json
import re
from typing import Dict


def extract_json_from_text(text: str) -> Dict:
    json_pattern = r'\{.*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)

    if matches:
        # 尝试每个匹配
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                try:
                    # 尝试修复常见的JSON格式问题
                    match = match.replace("'", '"')
                    match = re.sub(r',\s*}', '}', match)
                    match = re.sub(r',\s*]', ']', match)
                    return json.loads(match)
                except:
                    continue
    return None