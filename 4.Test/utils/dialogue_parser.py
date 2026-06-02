import json
from typing import Dict,List

def parse_dialogue_jsonl(file_path: str) -> List[Dict]:
    """解析jsonl对话文件"""
    dialogues = []
    with open(file_path, 'r', encoding='utf-8') as f:
    #with：上下文管理器，确保文件在使用后自动关闭。
    #open(file_path,'r',encoding='utf-8'):以只读r的方式，指定文件编码utf-8，打开文件file_path
        for line in f:
            if line.strip():
                #strip():移除str首尾的空白字符，例如空格、'\t'、'\n'等
                data = json.loads(line.strip())
                #利用json库中的loads()方法加载json数据。返回的data是字典类型。


                # 提取所需字段,类型为字典。
                dialogue = {
                    "round_number": data.get("round_number", 0),
                    "dialogue": data.get("dialogue", ""),
                    "is_key": data.get("is_key", "false"),
                    "reason": data.get("reason", "")
                }
                #.get(key, default)方法，提取data中key对应的value。若key缺失，返回default。


                dialogues.append(dialogue)
                #向列表dialogues中添加字典dialogue

    # 按轮次排序
    dialogues.sort(key=lambda x: x["round_number"])
    #.sort:列表的排序方法。
    #key= 的作用是：参数为一个函数，对列表中每个元素调用一个函数，用返回值作为排序依据。
    #lambda x: x["round_number"]  lambda函数，x为参数，返回x的round_number键的值。
    #每次取列表中的一个值作为x，然后取x中的round_number键的值
    return dialogues