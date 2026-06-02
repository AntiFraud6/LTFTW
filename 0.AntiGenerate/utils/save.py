#utils/save.py
import json
import os
import pandas as pd
def save_dialogue_to_csv(dialogue_history, background_idx, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    # 准备CSV文件路径
    output_filename = os.path.join(output_dir, f'dialogue_background_{background_idx + 1}.csv')

    if dialogue_history and isinstance(dialogue_history[0], dict):
        df = pd.DataFrame(dialogue_history)

        expected_columns = ['round_number', 'speaker', 'content',  'is_key', 'reason']
        for col in expected_columns:
            if col not in df.columns:
                df[col] = ''  # 添加缺失的列

        df.to_csv(output_filename, index=False, encoding='utf-8')
        print(f"对话结果已保存至: {output_filename}")

        json_filename = os.path.join(output_dir, f'dialogue_background_{background_idx + 1}.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(dialogue_history, f, ensure_ascii=False, indent=2)
        print(f"JSON备份已保存至: {json_filename}")

    else:
        print("警告：对话历史格式不正确，无法保存")