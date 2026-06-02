# utils/annotator.py
import asyncio
from typing import List, Dict, Any
from utils.parse_json import parse_json_response
from config.prompt import USER_PROMPT_TEMPLATE, SYSTEM_PROMPT


async def annotate_block(agent, block_data: Dict[str, Any]) -> Dict[str, Any]:
    """异步标注单个block"""
    i = block_data["block_index"]
    user_prompt = SYSTEM_PROMPT + USER_PROMPT_TEMPLATE.format(
        history_blocks=block_data["history_context"],
        current_block=block_data["current_block"],
        i=i,
        prev_R=block_data["prev_R"],
        prev_T=block_data["prev_T"]
    )

    print(f"正在处理Block {i}, 轮次: {block_data['block_range']}")

    try:
        response = await asyncio.to_thread(agent.instruct(user_prompt).start)
        annotation = parse_json_response(response)
        print(annotation)

        for key, value in annotation.items():
            if key != "block_range":
                block_data[key] = value

        return block_data
    except Exception as e:
        print(f"处理Block {i}时出错: {e}")
        block_data["error"] = str(e)
        return block_data


async def annotate_blocks_async(block_data_list: List[Dict[str, Any]],
                               agent,
                               max_concurrent: int = 5) -> List[Dict[str, Any]]:
    """异步处理单个文件的所有blocks"""
    results = []
    prev_R, prev_T = 0.001, 0.001

    for i, block_data in enumerate(block_data_list):
        block_data["prev_R"] = round(prev_R, 3)
        block_data["prev_T"] = round(prev_T, 3)

        result = await annotate_block(agent, block_data)
        results.append(result)

        # 更新状态
        prev_R = round(result.get("R", prev_R), 3)
        prev_T = round(result.get("T", prev_T), 3)

    return results