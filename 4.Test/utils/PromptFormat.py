from config.prompt import USER_PROMPT_TEMPLATE
def generate_prompt(history: str, current_block: str, block_idx: int, last_block_data: dict = None) -> str:
    if last_block_data is None:
        last_block_data = {"L_f": 0.1, "L_n": 0.1, "L_t": 0.1, "L_s": 0.1}

    return USER_PROMPT_TEMPLATE.format(
        history_blocks=history,
        current_block=current_block,
        i=block_idx,
        L_f=last_block_data.get("L_f", 0.5),
        L_n=last_block_data.get("L_n", 0.5),
        L_t=last_block_data.get("L_t", 0.5),
        L_s=last_block_data.get("L_s", 0.5)
    )
