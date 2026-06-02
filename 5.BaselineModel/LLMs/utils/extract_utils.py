# utils/extract_utils.py
import json
import re
from typing import Dict

def extract_json_from_text(text: str) -> Dict:
    json_pattern = r'\{.*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)

    if matches:
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                try:
                    match = match.replace("'", '"')
                    match = re.sub(r',\s*}', '}', match)
                    match = re.sub(r',\s*]', ']', match)
                    return json.loads(match)
                except:
                    continue
    return None