import os
import csv
import json
from pathlib import Path

def process_files(csv_dir, jsonl_dir, output_dir):
    """
    处理CSV和JSONL文件，生成对应的结果文件
    
    参数:
        csv_dir: CSV文件目录路径
        jsonl_dir: JSONL文件目录路径
        output_dir: 输出目录路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有jsonl文件
    jsonl_files = list(Path(jsonl_dir).glob("*.jsonl"))
    
    for jsonl_file in jsonl_files:
        # 获取文件名（不带后缀）
        file_name = jsonl_file.stem
        
        # 构建对应的CSV文件名
        csv_filename = f"{file_name}.csv"
        csv_file = Path(csv_dir) / csv_filename
        
        # 检查对应的CSV文件是否存在
        if not csv_file.exists():
            print(f"警告: 找不到对应的CSV文件: {csv_file}")
            continue
        
        # 从JSONL文件读取真实标签
        true_labels = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # 跳过空行
                    data = json.loads(line.strip())
                    true_labels.append(data.get("HighDanger", False))
        
        # 从CSV文件读取预测标签
        pred_labels = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                # 将字符串"True"/"False"转换为布尔值
                high_danger = row.get("HighDanger", "").lower() == "true"
                pred_labels.append(high_danger)
        
        # 检查行数是否匹配，不匹配时以行数少的为准
        if len(true_labels) != len(pred_labels):
            print(f"警告: 文件 {file_name} 行数不匹配! 将以行数少的为准进行处理")
            print(f"  JSONL行数: {len(true_labels)}")
            print(f"  CSV行数: {len(pred_labels)}")
            
            # 取较小的行数
            min_rows = min(len(true_labels), len(pred_labels))
            print(f"  将使用前 {min_rows} 行数据")
            
            # 截断多余的部分
            true_labels = true_labels[:min_rows]
            pred_labels = pred_labels[:min_rows]
        
        # 准备输出数据
        output_data = []
        for true_bool, pred_bool in zip(true_labels, pred_labels):
            # 将布尔值转换为0/1
            true_label = 1 if true_bool else 0
            pred_label = 1 if pred_bool else 0
            
            output_data.append({
                "true_label": true_label,
                "predicted_label": pred_label,
                "true_bool": true_bool,
                "pred_bool": pred_bool
            })
        
        # 构建输出文件路径
        output_file = Path(output_dir) / f"{file_name}.csv"
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["true_label", "predicted_label", "true_bool", "pred_bool"]
            csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # 写入表头
            csv_writer.writeheader()
            
            # 写入数据
            csv_writer.writerows(output_data)

# 使用示例
if __name__ == "__main__":
    # 路径设置
    csv_dir = r"D:\Study\SCI\Dataset\4.PredDanger\8B-Base-NoBayesian\0.Initial"
    jsonl_dir = r"D:\Study\SCI\Dataset\3.TrueDanger\Test"
    output_dir = r"D:\Study\SCI\Dataset\4.PredDanger\8B-Base-NoBayesian\1.Finally"
    
    # 处理文件
    process_files(csv_dir, jsonl_dir, output_dir)