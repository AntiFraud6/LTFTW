# utils/PromptFormat.py
from config.prompt import USER_PROMPT_TEMPLATE

def generate_prompt(history: str, current_block: str, block_idx: int, last_block_data: dict = None) -> str:
    return USER_PROMPT_TEMPLATE.format(
        history_blocks=history,
        current_block=current_block
    )