# #utils/csv_handler
import csv
import os
from typing import List, Dict
#
#
# def save_results_to_csv(results: List[Dict], output_path: str):
#     """将结果保存为CSV文件"""
#     if not results:
#         return
#
#     # 确保目录存在
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#
#     # 提取所有可能的字段
#     all_fields = set()
#     for result in results:
#         all_fields.update(result.keys())
#
#     # 定义字段顺序
#     field_order = [
#         'block_range', 'scam_strategy', 'cot_reasoning',
#         'qualitative_logic_8B.instruction', 'qualitative_logic_8B.logic_chain', 'qualitative_logic_8B.trend_analysis',
#         'L_f', 'L_n', 'L_t', 'L_s', 'risk_ratio (L_f/L_n)', 'trust_ratio (L_t/L_s)'
#     ]
#
#     # 实际使用的字段
#     fields = [f for f in field_order if f in all_fields]
#
#     with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=fields)
#         writer.writeheader()
#
#         for result in results:
#             # 展平qualitative_logic_8B字段
#             row = result.copy()
#             if 'qualitative_logic_8B' in row and isinstance(row['qualitative_logic_8B'], dict):
#                 logic_data = row.pop('qualitative_logic_8B')
#                 row['qualitative_logic_8B.instruction'] = logic_data.get('instruction', '')
#                 row['qualitative_logic_8B.logic_chain'] = logic_data.get('logic_chain', '')
#                 row['qualitative_logic_8B.trend_analysis'] = logic_data.get('trend_analysis', '')
#
#             writer.writerow(row)


def save_results_to_csv(results: List[Dict], output_path: str):
    """将结果保存为CSV文件（简化版）"""
    if not results:
        return

    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 使用第一个结果的所有键作为字段名
    fieldnames = list(results[0].keys())

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)