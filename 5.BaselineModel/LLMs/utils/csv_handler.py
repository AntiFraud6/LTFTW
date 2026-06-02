# utils/csv_handler.py
import csv
import os
from typing import List, Dict


def save_results_to_csv(results: List[Dict], output_path: str):
    if not results:
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 强制指定仅输出这两个字段（不再动态获取）
    fieldnames = ["block_range", "HighDanger"]

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)