#ConvertClean/clean.py
#用于清洗模型返回的数据
#Used to clean the data returned by the model
import re

def clean_content(text):

    # 1. 移除所有括号及内容（支持中文括号）
    text = re.sub(r'\([^)]*\)|（[^）]*）', '', text)

    # 2. 移除所有英文句点
    text = text.replace('.', '')

    # 3. 移除中文省略号
    text = text.replace('…', '')

    # 4. 移除"额"和"呃"
    text = text.replace('额', '').replace('呃', '')

    # 5. 移除连续两个及以上逗号（中英文）
    text = re.sub(r'[，,]{2,}', '', text)

    # 6. 规范化空格：多个连续空格转为单个空格，并去除首尾空格
    text = re.sub(r'\s+', ' ', text).strip()

    return text