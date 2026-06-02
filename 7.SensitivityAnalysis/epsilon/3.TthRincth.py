#计算Rinth(Tth)等。
import pandas as pd
import numpy as np
from pathlib import Path

# 读取数据
df = pd.read_csv(
    r"D:\Study\SCI\Dataset\SensitivityAnalysis\Block\Size5\3.TrueDanger\1.Statistics.csv"
)


prefix_list = {
    "All": "",
    "DouBaoDialogue": "DouBaoDialogue",
    "GeminiDialogue": "GeminiDialogue",
    "GPTDialogue": "GPTDialogue"
}

def compute_stats(df_subset, prefix_name):
    # 1. T 中位数（去重）
    t_unique = df_subset['T'].dropna().unique()
    t_median = np.median(t_unique) if len(t_unique) > 0 else None

    # 2. 每个 file 的 R 增幅中位数
    file_growth_medians = []

    for file_name, group in df_subset.groupby('file'):
        stage_filtered = group[group['stage'].isin(['Start_scamming', 'Harvest_exit'])]
        if len(stage_filtered) < 2:
            continue

        stage_filtered = stage_filtered.sort_values('line')
        r_values = stage_filtered['R'].values
        growth_rates = np.diff(r_values) / r_values[:-1]

        if len(growth_rates) == 0:
            continue

        unique_growth_rates = np.unique(growth_rates)
        remove_count = max(1, int(len(unique_growth_rates) * 0.05))
        trimmed_growth = np.sort(unique_growth_rates)[remove_count:]

        if len(trimmed_growth) > 0:
            file_growth_medians.append(np.median(trimmed_growth))

    # 3. 所有文件增幅中位数（去重）
    if len(file_growth_medians) > 0:
        unique_file_growth_medians = np.unique(file_growth_medians)
        r_median = np.median(unique_file_growth_medians)
    else:
        r_median = None

    return {
        "prefix": prefix_name,
        "t_median": t_median,
        "t_count": len(t_unique),
        "r_median": r_median,
        "file_count": len(file_growth_medians),
        "r_unique_count": len(unique_file_growth_medians) if len(file_growth_medians) > 0 else 0
    }

output_path = r"D:\Study\SCI\Dataset\SensitivityAnalysis\Block\Size5\3.TrueDanger\result.txt"

with open(output_path, 'w', encoding='utf-8') as f:
    for prefix_name, prefix_str in prefix_list.items():
        if prefix_name == "All":
            df_sub = df
        else:
            df_sub = df[df['file'].str.startswith(prefix_str)]

        stats = compute_stats(df_sub, prefix_name)

        f.write(f"\n===== {stats['prefix']} =====\n")
        f.write(f"T值中位数(去重后): {stats['t_median']}\n")
        f.write(f"T值唯一值数量: {stats['t_count']}\n")
        f.write(f"R增幅中位数(去重后): {stats['r_median']}\n")
        f.write(f"处理文件数量: {stats['file_count']}\n")
        f.write(f"文件增幅中位数唯一值数量: {stats['r_unique_count']}\n")

print("统计完成")