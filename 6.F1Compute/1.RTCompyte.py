#输入模型Pred原始返回
import pandas as pd
import os
import numpy as np


def calculate_r_t(row, prev_r, prev_t):
    """根据公式计算R和T值"""
    # 从行中提取L值
    L_f = row['L_f']
    L_n = row['L_n']
    L_t = row['L_t']
    L_s = row['L_s']

    # 计算R_i
    numerator_r = L_f * prev_r
    denominator_r = L_f * prev_r + L_n * (1 - prev_r)
    R_i = numerator_r / denominator_r if denominator_r != 0 else prev_r

    # 计算T_i
    numerator_t = L_t * prev_t
    denominator_t = L_t * prev_t + L_s * (1 - prev_t)
    T_i = numerator_t / denominator_t if denominator_t != 0 else prev_t

    # 限制范围在(0.001, 0.999)
    R_i = np.clip(R_i, 0.001, 0.999)
    T_i = np.clip(T_i, 0.001, 0.999)

    return R_i, T_i, prev_r, prev_t


def process_csv_files(source_dir, target_dir):
    """处理所有CSV文件"""
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 获取所有CSV文件
    csv_files = [f for f in os.listdir(source_dir) if f.endswith('.csv')]

    for csv_file in csv_files:
        source_path = os.path.join(source_dir, csv_file)
        target_path = os.path.join(target_dir, csv_file)

        print(f"处理文件: {csv_file}")

        # 读取CSV文件
        df = pd.read_csv(source_path)

        # 初始化prev_R和prev_T
        prev_R = 0.001
        prev_T = 0.001

        # 存储计算结果
        R_values = []
        T_values = []
        prev_R_values = []
        prev_T_values = []

        # 遍历每一行进行计算
        for idx, row in df.iterrows():
            # 记录当前行的prev_R和prev_T
            prev_R_values.append(prev_R)
            prev_T_values.append(prev_T)

            # 计算R和T
            R_i, T_i, prev_R_for_row, prev_T_for_row = calculate_r_t(row, prev_R, prev_T)

            # 保留3位小数
            R_i = round(R_i, 3)
            T_i = round(T_i, 3)

            # 存储结果
            R_values.append(R_i)
            T_values.append(T_i)

            # 更新prev_R和prev_T为当前行计算结果
            prev_R = R_i
            prev_T = T_i

        # 添加新列到DataFrame
        df['prev_R'] = prev_R_values
        df['prev_T'] = prev_T_values
        df['R'] = R_values
        df['T'] = T_values

        # 保存到目标目录，修改编码为utf-8-sig
        df.to_csv(target_path, index=False, float_format='%.3f', encoding='utf-8-sig')
        print(f"  已保存到: {target_path}")

    print(f"\n处理完成！共处理 {len(csv_files)} 个文件")


# 使用示例
source_directory = r"D:\Study\SCI\Dataset\SensitivityAnalysis\Block\Size15\4.PredDanger\0.InitialData"
target_directory = r"D:\Study\SCI\Dataset\SensitivityAnalysis\Block\Size15\4.PredDanger\1.ProcessedData"

process_csv_files(source_directory, target_directory)