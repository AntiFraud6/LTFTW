#utils/ParseJson
import json
from typing import Dict, Any

def parse_json_response(response: str) -> Dict[str, Any]:
    """解析JSON响应，解析失败时抛出异常"""
    try:
        # 提取JSON部分，去掉冗余回答
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].strip()
        else:
            json_str = response.strip()
        return json.loads(json_str)
        #将json字符串转化为json格式。
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"原始响应: {response}")
        #修复常见的JSON格式问题
        try:
            json_str = response.replace("'", '"').replace("True", "true").replace("False", "false")
            #将 ' 替换为 "
            #将大写的True/false替换为小写的true/false
            return json.loads(json_str)
        except Exception as fix_e:
            print(f"JSON修复失败: {fix_e}")
            #抛出异常而不是返回错误字典

            raise json.JSONDecodeError(f"JSON解析失败: {fix_e}", doc=response, pos=0) from fix_e