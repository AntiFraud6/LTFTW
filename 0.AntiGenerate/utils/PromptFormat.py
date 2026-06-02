#utils/PromptFormat
def format_prompt(template: str, **kwargs) -> str:
    """
    安全地格式化提示词模板，处理可能的格式化错误
    template: 提示词模板
    **kwargs: 需要填充的参数
    Returns:格式化后的提示词
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        print(f"提示词格式化错误 - 缺少参数: {e}")
        # 返回原始模板并添加错误信息
        return template + f"\n\n[ERROR: Missing parameter {e}]"
    except Exception as e:
        print(f"提示词格式化错误: {e}")
        return template + f"\n\n[ERROR: Formatting failed - {e}]"