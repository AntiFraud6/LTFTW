# data_loader.py
import os
import jsonlines
import pandas as pd
from config import DATA_DIR, TEST_SIZE, RANDOM_STATE
import random

def load_data_by_files():
    """按文件划分训练集和测试集"""
    # 获取所有jsonl文件
    all_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".jsonl")]
    all_files.sort()  # 排序确保可重复性
    
    # 随机打乱文件
    random.seed(RANDOM_STATE)
    shuffled_files = all_files.copy()
    random.shuffle(shuffled_files)
    
    # 按比例划分文件
    split_index = int(len(shuffled_files) * (1 - TEST_SIZE))
    train_files = shuffled_files[:split_index]
    test_files = shuffled_files[split_index:]
    
    print(f"Train files: {len(train_files)} files")
    print(f"Test files: {len(test_files)} files")
    
    return train_files, test_files


def load_specific_file(filename):
    """加载指定的单个文件"""
    data = []
    filepath = os.path.join(DATA_DIR, filename)
    
    with jsonlines.open(filepath) as f:
        for line in f:
            data.append({
                "text": line["current_block"],
                "label": 1 if line["HighDanger"] else 0
            })
    
    return pd.DataFrame(data)
