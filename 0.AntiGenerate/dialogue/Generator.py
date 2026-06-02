#dialogue/Generator.py
#生成器，生成对话。
#Generator, generate dialogue.
import json
from typing import List, Dict
from utils.PromptFormat import format_prompt
from utils.ParseJson import parse_json_response
import os
max_retries = 10


async def generate_dialogue_chunk_async(gemini_agent, background: str, dialogue_history: List[Dict],
                                        feedback: str, start_round: int, chunk_size: int,
                                        stage_prompt_template: str, stage_name: str) -> List[Dict]:
    """异步生成一个对话块"""

    # 1. 构建对话历史字符串
    history_str = ""
    if dialogue_history:
        history_str = "\n".join([
            f" [{dialogue['speaker']}]: {dialogue['content']} "
            for dialogue in dialogue_history
        ])

    # 2. 格式化阶段指令
    stage_instructions = format_prompt(
        stage_prompt_template,
        target_rounds=chunk_size
    )

    # 3. 组合提示词
    from config.prompt import GEMINI_SYSTEM_PROMPT_TEMPLATE
    combined_prompt = format_prompt(
        GEMINI_SYSTEM_PROMPT_TEMPLATE,
        stage_instructions=stage_instructions,
        background=background,
        dialogue_history=history_str,
        feedback=feedback if feedback else "无反馈",
        chunk_size=chunk_size
    )

    combined_prompt += f"\n\n请严格按照上述要求生成第{start_round + 1}到{start_round + chunk_size}轮对话，返回JSON数组格式。"

    # 4. 重试机制
    for attempt in range(max_retries):
        try:
            print(f"进程 {os.getpid()} - 第{attempt + 1}次尝试生成对话:")

            # 使用传入的agent实例
            response = await gemini_agent.instruct(combined_prompt).start_async()

            if "[" in response and "]" in response:
                json_str = response[response.index("["):response.rindex("]") + 1]
                dialogues = json.loads(json_str)
            else:
                dialogues = parse_json_response(response)

            print(f'进程 {os.getpid()} - json解析成功')

            if isinstance(dialogues, dict):
                dialogues = [dialogues]

            # 验证和修复每个对话项
            validated_dialogues = []
            for i, dialogue in enumerate(dialogues):
                if not isinstance(dialogue, dict):
                    continue
                validated_dialogue = {
                    'round_number': dialogue.get('round_number', start_round + i + 1),
                    'speaker': dialogue.get('speaker', '诈骗者' if i % 2 == 0 else '受害者'),
                    'content': dialogue.get('content', ''),
                    'stage': stage_name,
                    'is_key': dialogue.get('is_key', '否'),
                    'reason': dialogue.get('reason', '')
                }
                validated_dialogues.append(validated_dialogue)

            print(f"进程 {os.getpid()} - 第{attempt + 1}次尝试生成对话成功!")
            return validated_dialogues

        except Exception as e:
            print(f"进程 {os.getpid()} - 生成对话时出错，第{attempt + 1}次尝试失败: {e}")
            if attempt == max_retries - 1:
                raise Exception(f"生成对话失败，已重试{max_retries}次") from e


# 保持原有同步函数兼容性
def generate_dialogue_chunk(background: str, dialogue_history: List[Dict],
                            feedback: str, start_round: int, chunk_size: int,
                            stage_prompt_template: str, stage_name: str) -> List[Dict]:
    """同步版本的生成函数（兼容原有代码）"""
    import asyncio
    from agents.create import AgentFactory

    # 创建agent实例
    agent_factory = AgentFactory()
    gemini_agent = agent_factory.create_agent('Gemini')

    # 调用异步版本
    return asyncio.run(generate_dialogue_chunk_async(
        gemini_agent, background, dialogue_history, feedback,
        start_round, chunk_size, stage_prompt_template, stage_name
    ))