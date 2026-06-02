#json格式打label
import json
import os
import glob

# 定义输入和输出目录路径
input_dir = r"D:\Study\SCI\Dataset\SensitivityAnalysis\Block\Size15\1.Annotation\1.All"
output_dir = r"D:\Study\SCI\Dataset\SensitivityAnalysis\Block\Size15\3.TrueDanger"

# 创建输出目录（如果不存在）
os.makedirs(output_dir, exist_ok=True)

# 获取所有jsonl文件
jsonl_files = glob.glob(os.path.join(input_dir, "*.jsonl"))

# 处理每个jsonl文件
for jsonl_file in jsonl_files:
    # 读取jsonl文件的所有行
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    processed_data = []
    prev_R = None

    for i, line in enumerate(lines):
        data = json.loads(line.strip())

        # 提取R和T值
        current_R = float(data['R'])
        current_T = float(data['T'])

        # 第一个默认标为false
        if i == 0:
            data['HighDanger'] = False
            prev_R = current_R
        else:
            # 计算相对增幅
            if prev_R != 0:
                R_increase = (current_R - prev_R) / prev_R
            else:
                R_increase = 0

            # 根据规则判断HighDanger
            if current_T > 0.53 and R_increase > 0.35:
                data['HighDanger'] = True
            elif current_T > 0.53 and current_R > 0.74:
                data['HighDanger'] = True
            else:
                data['HighDanger'] = False

            prev_R = current_R

        processed_data.append(data)

    # 构建输出文件路径
    file_name = os.path.basename(jsonl_file)
    output_path = os.path.join(output_dir, file_name)

    # 写入新的jsonl文件
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in processed_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"已处理文件: {file_name}")

print(f"\n处理完成！文件已保存到: {output_dir}")