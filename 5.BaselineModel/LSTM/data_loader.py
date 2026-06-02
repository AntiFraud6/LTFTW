import json
import os
import pandas as pd
import random


def load_jsonl_files(directory):
    """加载目录下所有jsonl文件"""
    data = []
    for filename in os.listdir(directory):
        if filename.endswith('.jsonl'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        item = json.loads(line.strip())
                        # 合并history_context和current_block
                        text = item['history_context'] + " " + item['current_block']
                        label = int(item['HighDanger'])
                        data.append({'text': text, 'label': label})
                    except json.JSONDecodeError:
                        continue
    return pd.DataFrame(data)


def load_specific_file(filepath):
    """加载单个jsonl文件"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line.strip())
                text = item['history_context'] + " " + item['current_block']
                label = int(item['HighDanger'])
                data.append({'text': text, 'label': label})
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(data)


def prepare_data(train_dir, test_dir):
    """准备训练和测试数据"""
    print("Loading training data...")
    train_df = load_jsonl_files(train_dir)
    print(f"Loaded {len(train_df)} training samples")

    print("Loading test data...")
    test_df = load_jsonl_files(test_dir)
    print(f"Loaded {len(test_df)} test samples")

    return train_df, test_df