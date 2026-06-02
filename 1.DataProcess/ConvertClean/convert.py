#将模型返回的csv文件转换成jsonl格式
#Convert the CSV file returned by the model into JSONL format
import os
import csv
import json
from ConvertClean.clean import clean_content
def process_directory(input_dir, output_dir):
    """处理指定目录下的所有CSV文件"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 统计信息
    total_files = 0
    total_rows = 0
    filtered_empty = 0

    # 遍历输入目录中的所有CSV文件
    for filename in os.listdir(input_dir):
        if not filename.endswith('.csv'):
            continue

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.jsonl')

        with open(input_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            json_lines = []
            file_rows = 0
            file_filtered = 0

            for row in reader:
                total_rows += 1
                file_rows += 1

                # 转换轮数为整数
                try:
                    round_num = int(row['round_number'])
                except (ValueError, KeyError):
                    print(f"警告: 文件 {filename} 中轮数格式错误，跳过该行: {row}")
                    continue

                #（诈骗者→A，受害者→B）
                speaker_map = {'诈骗者': 'A', '受害者': 'B'}
                new_speaker = speaker_map.get(row['speaker'], row['speaker'])

                # 清理对话内容
                cleaned_content = clean_content(row['content'])

                # 过滤空对话：清洗后内容为空则跳过
                if not cleaned_content:
                    filtered_empty += 1
                    file_filtered += 1
                    continue

                # 组装对话格式
                dialogue = f"{new_speaker}: {cleaned_content}"

                # 构建JSON对象
                json_obj = {
                    "round_number": round_num,
                    "dialogue": dialogue
                }
                json_lines.append(json.dumps(json_obj, ensure_ascii=False))

            # 写入JSONL文件（即使为空文件也创建）
            with open(output_path, 'w', encoding='utf-8') as jsonl_file:
                if json_lines:
                    jsonl_file.write('\n'.join(json_lines))

            total_files += 1
            print(f"处理完成: {filename} -> {os.path.basename(output_path)} "
                  f"(保留{len(json_lines)}行，过滤{file_filtered}空行)")

    # 打印统计信息
    print(f"处理完成！共处理 {total_files} 个CSV文件")
    print(f"原始总行数: {total_rows}")
    print(f"过滤空对话: {filtered_empty}")
    print(f"有效输出行数: {total_rows - filtered_empty}")
    print(f"输出目录: {output_dir}")
    print("=" * 60)