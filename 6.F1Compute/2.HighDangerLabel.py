#csv格式打label
import pandas as pd
import os
import glob


# 定义输入和输出目录路径
input_dir = r"xxx\4.PredDanger\1.ProcessedData"
output_dir = r"xxx\4.PredDanger\2.LabelData"

# 创建输出目录（如果不存在）
os.makedirs(output_dir, exist_ok=True)

# 获取所有csv文件
csv_files = glob.glob(os.path.join(input_dir, "*.csv"))

# 处理每个csv文件
for csv_file in csv_files:
    # 读取csv文件
    df = pd.read_csv(csv_file)

    # 确保R和T是数值类型
    df['R'] = pd.to_numeric(df['R'])
    df['T'] = pd.to_numeric(df['T'])

    # 初始化HighDanger列
    high_danger = []

    # 遍历每一行，判断HighDanger
    for i in range(len(df)):
        current_R = df.loc[i, 'R']
        current_T = df.loc[i, 'T']

        # 获取上一行的R值
        if i > 0:
            prev_R = df.loc[i - 1, 'R']
        else:
            prev_R = current_R  # 第一行没有上一行，设为当前值

        # 计算R的相对增幅（改为相对增幅，处理除零情况）
        if i > 0 and prev_R != 0:
            R_increase = (current_R - prev_R) / prev_R
        else:
            R_increase = 0  # 第一行或上一行R为0时，增幅为0

        # 根据条件判断HighDanger
        if current_T > 0.53 and R_increase > 0.35:
            high_danger.append(True)
        elif current_T > 0.53 and current_R > 0.74:
            high_danger.append(True)
        else:
            high_danger.append(False)

    # 添加HighDanger列
    df['HighDanger'] = high_danger

    # 构建输出文件路径
    file_name = os.path.basename(csv_file)
    output_path = os.path.join(output_dir, file_name)

    # 保存到输出目录，使用utf-8-sig编码
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"已处理文件: {file_name}")

print(f"\n处理完成！文件已保存到: {output_dir}")
