#将原始csv文件转换为jsonl文件。csv文件为DeepSeek-Reasoner原始返回，而生成jsonl带R和T（通过代码递归计算，而不是读取之前的prev_R prev_T）。
#保存至1.Annotation目录
import pandas as pd
import os
import glob
import re  # 导入正则表达式库


def clean_text(text):
    """
    清洗文本，去除 Blockx (轮次 xx-xx):\n 格式的字符串
    """
    if pd.isna(text):
        return text

    # 正则表达式模式：匹配 "Block数字 (轮次 数字-数字):\n"
    # \s* 表示可能存在的空格
    pattern = r'Block\d+\s*\(轮次\s*\d+-\d+\):\n'

    # 将匹配到的内容替换为空字符串
    cleaned_text = re.sub(pattern, '', str(text))
    return cleaned_text


def recalc_r_t(epsilon, input_dir, output_base_dir):
    """重新计算单个ε值下的R和T，保存为JSONL格式，保留3位小数"""
    # 创建输出目录
    output_dir = os.path.join(output_base_dir, f"eps_{epsilon}")
    os.makedirs(output_dir, exist_ok=True)

    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))

    for file in csv_files:
        df = pd.read_csv(file)

        if 'history_context' in df.columns:
            df['history_context'] = df['history_context'].apply(clean_text)

        if 'current_block' in df.columns:
            df['current_block'] = df['current_block'].apply(clean_text)

        # 初始化第一行的R和T值为epsilon
        prev_R = epsilon
        prev_T = epsilon

        # 创建新的R和T列
        new_R = []
        new_T = []

        for idx, row in df.iterrows():
            # 使用上一行计算的R和T（第一行使用epsilon作为初始值）
            L_f = row['L_f']
            L_n = row['L_n']
            L_t = row['L_t']
            L_s = row['L_s']

            # 计算当前行的R和T
            curr_R = (L_f * prev_R) / (L_f * prev_R + L_n * (1 - prev_R))
            curr_T = (L_t * prev_T) / (L_t * prev_T + L_s * (1 - prev_T))

            # 限制范围 (epsilon, 1-epsilon)
            curr_R = max(epsilon, min(1 - epsilon, curr_R))
            curr_T = max(epsilon, min(1 - epsilon, curr_T))

            # 保留3位小数
            curr_R = round(curr_R, 3)
            curr_T = round(curr_T, 3)

            new_R.append(curr_R)
            new_T.append(curr_T)

            # 更新prev_R和prev_T为当前行的值，用于下一行计算
            prev_R = curr_R
            prev_T = curr_T

        # 将新计算的R和T添加到DataFrame
        df['R'] = new_R
        df['T'] = new_T

        # 只保留指定的4个字段
        cols = ['history_context', 'current_block', 'R', 'T']
        available_cols = [c for c in cols if c in df.columns]

        df_out = df[available_cols]

        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(file))[0]
        output_path = os.path.join(output_dir, f"{base_name}.jsonl")

        # 保存为 JSON Lines 格式
        df_out.to_json(output_path, orient='records', lines=True, force_ascii=False)

    return output_dir


def batch_experiment(epsilon_list, input_dir, output_base_dir=None):
    """批量运行多个ε值实验"""
    if output_base_dir is None:
        output_base_dir = os.path.join(input_dir, "SensitivityResults")

    os.makedirs(output_base_dir, exist_ok=True)

    print(f"开始批量实验，共 {len(epsilon_list)} 个ε值")
    print(f"输入目录: {input_dir}")
    print("-" * 60)

    generated_dirs = []
    for i, eps in enumerate(epsilon_list, 1):
        print(f"[{i}/{len(epsilon_list)}] 正在处理 ε = {eps}")
        output_dir = recalc_r_t(eps, input_dir, output_base_dir)
        generated_dirs.append(output_dir)

    print("\n" + "=" * 60)
    print(f"所有实验完成！结果保存在: {output_base_dir}")

    return generated_dirs


if __name__ == "__main__":
    INPUT_DIR = r"D:\Study\SCI\Dataset\Ablation\DouBao\0.InitialData"

    EPSILON_LIST = [
        0.001
    ]

    batch_experiment(EPSILON_LIST, INPUT_DIR)