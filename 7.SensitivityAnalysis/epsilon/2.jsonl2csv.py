#将jsonl整合到一个csv文件，记录所有的R和T。
#保存至Annotation目录
import os
import csv
import json
import glob

# 目标目录路径
dir_path = r"D:\Study\SCI\Dataset\SensitivityAnalysis\Block\Size5\3.TrueDanger"
output_csv = os.path.join(dir_path, "1.Statistics.csv")

with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['file', 'line', 'R', 'T', 'stage'])  # 表头

    # 遍历所有jsonl文件
    for jsonl_file in glob.glob(os.path.join(dir_path, "*.jsonl")):
        filename = os.path.basename(jsonl_file)  # 仅保留文件名
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):  # 行号从1开始
                data = json.loads(line.strip())
                writer.writerow([filename, line_num, data['R'], data['T'], data['stage']])