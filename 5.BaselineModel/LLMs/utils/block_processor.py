# utils/block_processor.py
from typing import List, Dict
from .dialogue_parser import parse_dialogue_jsonl

def create_blocks(dialogues: List[Dict], block_size: int = 10) -> List[List[Dict]]:
    blocks = []
    for i in range(0, len(dialogues), block_size):
        block = dialogues[i:i + block_size]
        if len(block) == block_size:
            blocks.append(block)
    return blocks

def format_block_text(block: List[Dict]) -> str:
    return "\n".join([f"{dial['dialogue']}" for dial in block])

def get_history_context(blocks: List[List[Dict]], current_idx: int, history_len: int = 2) -> str:
    start_idx = max(0, current_idx - history_len)
    history_blocks = blocks[start_idx:current_idx]

    history_texts = []
    for idx, block in enumerate(history_blocks, start=start_idx + 1):
        block_start = idx * 10 - 9
        block_end = idx * 10
        history_texts.append(f"Block{idx} (轮次 {block_start}-{block_end}):")
        history_texts.append(format_block_text(block))

    return "\n".join(history_texts)

def process_sample(sample_path: str, block_size: int = 10, history_blocks: int = 2) -> List[Dict]:
    dialogues = parse_dialogue_jsonl(sample_path)
    blocks = create_blocks(dialogues, block_size)

    processed_data = []
    for i, block in enumerate(blocks):
        if i < 1:
            continue

        block_range = f"{i * 10 - 9}-{i * 10}"
        history = get_history_context(blocks, i, history_blocks)
        current_text = format_block_text(block)

        processed_data.append({
            "block_index": i + 1,
            "block_range": block_range,
            "history_context": history,
            "current_block": current_text
        })

    return processed_data