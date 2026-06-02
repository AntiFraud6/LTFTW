#取绝对值
import pandas as pd
import os
import numpy as np

# 设置目录路径
directory = r"D:\Study\SCI\Dataset\4.PredDanger\8B-Base-NoBayesian\1.Finally"

# 用于存储每个文件的结果
file_results = []
all_warn_early = []

print("各文件指标：")
print("-" * 50)

# 遍历目录中的所有csv文件
for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        filepath = os.path.join(directory, filename)
        df = pd.read_csv(filepath)

        # 计算该文件的TP, FP, TN, FN
        TP = ((df['true_bool'] == True) & (df['pred_bool'] == True)).sum()
        FP = ((df['true_bool'] == False) & (df['pred_bool'] == True)).sum()
        TN = ((df['true_bool'] == False) & (df['pred_bool'] == False)).sum()
        FN = ((df['true_bool'] == True) & (df['pred_bool'] == False)).sum()

        # 计算该文件的F1分数
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        # 计算该文件的FPR
        fpr = FP / (FP + TN) if (FP + TN) > 0 else 0

        # 计算该文件的WarnEarly（取绝对值）
        warn_early = np.nan
        pred_true_idx = df[df['pred_bool'] == True].index
        true_true_idx = df[df['true_bool'] == True].index

        if len(pred_true_idx) > 0 and len(true_true_idx) > 0:
            warn_early = abs(pred_true_idx[0] - true_true_idx[0])  # 取绝对值
            all_warn_early.append(warn_early)

        # 存储结果
        file_results.append({
            'filename': filename,
            'F1': f1,
            'FPR': fpr,
            'WarnEarly': warn_early
        })

        # 打印当前文件的结果
        print(f"文件: {filename}")
        print(f"  F1 Score: {f1:.4f}")
        print(f"  FPR: {fpr:.4f}")
        print(f"  WarnEarly: {warn_early:.2f}" if not np.isnan(warn_early) else "  WarnEarly: N/A")
        print("-" * 30)

# 计算平均指标
if file_results:
    avg_f1 = np.mean([r['F1'] for r in file_results])
    avg_fpr = np.mean([r['FPR'] for r in file_results])
    avg_warn_early = np.mean(all_warn_early) if all_warn_early else 0

    print("\n" + "=" * 50)
    print("所有文件的平均指标：")
    print(f"平均 F1 Score: {avg_f1:.4f}")
    print(f"平均 FPR: {avg_fpr:.4f}")
    print(f"平均 WarnEarly: {avg_warn_early:.2f}")
else:
    print("未找到CSV文件！")