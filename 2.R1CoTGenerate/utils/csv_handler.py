#utils/csv_handler.py
import os
import csv
from typing import List, Dict


def generate_output_filename(input_path: str, output_dir: str) -> str:
    """
    根据输入文件路径生成输出CSV文件名
    示例: dialogue_background_1.jsonl → dialogue_background_1_analysis.csv
    """
    # 获取输入文件名（不含路径）
    input_filename = os.path.basename(input_path)

    # 去除.jsonl后缀，添加_analysis.csv
    base_name = input_filename.replace('.jsonl', '')
    output_filename = f"{base_name}_analysis.csv"

    # 组合完整输出路径
    return os.path.join(output_dir, output_filename)


def save_results_to_csv(results: List[Dict], output_path: str):
    """将单个样本的结果保存为CSV文件"""
    if not results:
        print(f"警告: 无结果数据，跳过保存 {output_path}")
        return

    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 直接使用原始键名（移除列名映射逻辑）
        fieldnames = list(results[0].keys())

        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)  # 直接写入原始结果

        print(f"✓已保存: {output_path} (共{len(results)}行)")

    except Exception as e:
        print(f"✗保存失败 {output_path}: {e}")


def batch_save_samples(sample_data_dict: Dict[str, List[Dict]], output_dir: str):
    """
    批量保存多个样本到各自的CSV文件
    :param sample_data_dict: {样本路径: 处理后的数据列表}
    :param output_dir: 输出目录
    """
    print(f"开始批量保存到目录: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    saved_count = 0
    for sample_path, results in sample_data_dict.items():
        output_path = generate_output_filename(sample_path, output_dir)
        save_results_to_csv(results, output_path)
        saved_count += 1

    print(f"批量保存完成! 共处理{saved_count}个样本")













# #utils/csv_handler.py
# import os
# import csv
# from typing import List, Dict
#
#
# def generate_output_filename(input_path: str, output_dir: str) -> str:
#     """
#     根据输入文件路径生成输出CSV文件名
#     示例: dialogue_background_1.jsonl → dialogue_background_1_analysis.csv
#     """
#     # 获取输入文件名（不含路径）
#     input_filename = os.path.basename(input_path)
#
#     # 去除.jsonl后缀，添加_analysis.csv
#     base_name = input_filename.replace('.jsonl', '')
#     output_filename = f"{base_name}_analysis.csv"
#
#     # 组合完整输出路径
#     return os.path.join(output_dir, output_filename)
#
#
# def save_results_to_csv(results: List[Dict], output_path: str):
#     """将单个样本的结果保存为CSV文件"""
#     if not results:
#         print(f"警告: 无结果数据，跳过保存 {output_path}")
#         return
#
#     try:
#         # 确保输出目录存在
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)
#
#         # 定义列名映射：将可能的简化列名映射到完整列名
#         column_mapping = {
#             'risk_ratio': 'risk_ratio (L_f/L_n)',
#             'trust_ratio': 'trust_ratio (L_t/L_s)'
#         }
#
#         # 处理每个结果，统一列名格式
#         processed_results = []
#         for result in results:
#             processed_result = {}
#             for key, value in result.items():
#                 # 如果键在映射中，使用映射后的完整列名
#                 if key in column_mapping:
#                     processed_result[column_mapping[key]] = value
#                 else:
#                     processed_result[key] = value
#             processed_results.append(processed_result)
#
#         # 使用处理后的第一个结果的所有键作为字段名
#         fieldnames = list(processed_results[0].keys())
#
#         with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
#             writer = csv.DictWriter(f, fieldnames=fieldnames)
#             writer.writeheader()
#             writer.writerows(processed_results)
#
#         print(f"✓已保存: {output_path} (共{len(results)}行)")
#
#     except Exception as e:
#         print(f"✗保存失败 {output_path}: {e}")
#
#
# def batch_save_samples(sample_data_dict: Dict[str, List[Dict]], output_dir: str):
#     """
#     批量保存多个样本到各自的CSV文件
#     :param sample_data_dict: {样本路径: 处理后的数据列表}
#     :param output_dir: 输出目录
#     """
#     print(f"开始批量保存到目录: {output_dir}")
#     os.makedirs(output_dir, exist_ok=True)
#
#     saved_count = 0
#     for sample_path, results in sample_data_dict.items():
#         output_path = generate_output_filename(sample_path, output_dir)
#         save_results_to_csv(results, output_path)
#         saved_count += 1
#
#     print(f"批量保存完成! 共处理{saved_count}个样本")