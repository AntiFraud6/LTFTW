#为jsonl添加stage，以便后续计算R和T的中位数。
##保存至1.Annotation目录，添加了stage。
import json
import os

dir_a = r"D:\Study\SCI\Dataset\SensitivityAnalysis\YiPuXiLong\1.Annotation\eps_0.001"
dir_b = r"D:\Study\SCI\Dataset\1.Annotaion\1.All"

# 获取目录A中的所有jsonl文件
files_a = [f for f in os.listdir(dir_a) if f.endswith('.jsonl')]

for file_name in files_a:
    path_a = os.path.join(dir_a, file_name)
    path_b = os.path.join(dir_b, file_name)

    if not os.path.exists(path_b):
        print(f"警告: {file_name} 在目录B中不存在，已跳过")
        continue

    # 读取两个文件的所有行
    with open(path_a, 'r', encoding='utf-8') as f_a, \
            open(path_b, 'r', encoding='utf-8') as f_b:
        lines_a = f_a.readlines()
        lines_b = f_b.readlines()

    # 确定处理的行数（取较小值）
    min_lines = min(len(lines_a), len(lines_b))

    if len(lines_a) != len(lines_b):
        print(f"{file_name}: 行数不匹配 (A: {len(lines_a)}, B: {len(lines_b)})，仅处理前 {min_lines} 行")

    new_lines = []
    for i in range(min_lines):
        try:
            data_a = json.loads(lines_a[i].strip())
            data_b = json.loads(lines_b[i].strip())

            # 添加stage字段
            if 'stage' in data_b:
                data_a['stage'] = data_b['stage']
            else:
                data_a['stage'] = None  # 如果没有stage字段，设为None

            new_lines.append(json.dumps(data_a, ensure_ascii=False) + '\n')
        except json.JSONDecodeError as e:
            print(f"JSON解析错误 in {file_name} 第 {i + 1} 行: {e}")
            new_lines.append(lines_a[i])  # 保留原行

    # 如果有剩余行（A比B多），直接追加
    if len(lines_a) > min_lines:
        new_lines.extend(lines_a[min_lines:])

    # 写回文件A
    with open(path_a, 'w', encoding='utf-8') as f_a:
        f_a.writelines(new_lines)

print("处理完成！")