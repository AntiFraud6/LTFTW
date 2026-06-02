# config/prompt.py

USER_PROMPT_TEMPLATE = """

历史对话：
{history_blocks}

当前对话块：
{current_block}
上面是一段对话文本, 请结合历史对话和当前对话块分析对话内容是否为高危诈骗，只以json格式输出你的判断结果(HighDanger: true/false)。注意，只输出json格式的(HighDanger: true/false)即可，别的一概不输出。"""