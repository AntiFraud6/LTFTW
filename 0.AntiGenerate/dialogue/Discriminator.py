# dialogue/Discriminator.py
#判别器，判别是否为对话。
#Discriminator, to determine whether it is a conversation
from typing import List, Dict, Any
from config.prompt import V3_SYSTEM_PROMPT_TEMPLATE
from utils.PromptFormat import format_prompt
from utils.ParseJson import parse_json_response
import os
max_retries = 5


async def detect_fraud_async(v3_agent, dialogues: List[Dict]) -> Dict[str, Any]:
    """使用v3异步检测诈骗特征"""
    dialogues_str = "\n".join([
        f"[{dialogue['speaker']}]: {dialogue['content']} "
        for dialogue in dialogues
    ])

    # 格式化检测提示词
    prompt = format_prompt(V3_SYSTEM_PROMPT_TEMPLATE) + f"\n\n请分析以下对话：\n{dialogues_str}"

    for attempt in range(max_retries):
        try:
            # 使用传入的agent实例
            response = await v3_agent.instruct(prompt).start_async()
            return parse_json_response(response)
        except Exception as e:
            print(f"进程 {os.getpid()} - v3判别对话时出错，第{attempt + 1}次尝试失败: {e}")
            if attempt == max_retries - 1:
                raise Exception(f"生成对话失败，已重试{max_retries}次") from e


# 保持原有同步函数兼容性
def detect_fraud(dialogues: List[Dict]) -> Dict[str, Any]:
    """同步版本的检测函数（兼容原有代码）"""
    import asyncio
    from agents.create import AgentFactory

    # 创建agent实例
    agent_factory = AgentFactory()
    v3_agent = agent_factory.create_agent('DeepSeekv3')

    # 调用异步版本
    return asyncio.run(detect_fraud_async(v3_agent, dialogues))