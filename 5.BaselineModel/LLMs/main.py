import os
import time
import re
from utils.block_processor import process_sample
from utils.PromptFormat import generate_prompt
from utils.extract_utils import extract_json_from_text
from utils.csv_handler import save_results_to_csv
from agents.agent_factory import AgentFactory

def main():
    # 配置
    MODEL_NAME = "qwen"
    INPUT_DIR = r""
    OUTPUT_ROOT_DIR = AgentFactory.get_output_dir(MODEL_NAME)
    os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)

    # 1. 创建Agent
    agent = AgentFactory.create_agent(MODEL_NAME)
    print("Agent OK")

    # 2. 遍历目录下每个 jsonl 文件
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".jsonl"):
            file_path = os.path.join(INPUT_DIR, filename)
            csv_filename = os.path.splitext(filename)[0] + ".csv"
            output_file_path = os.path.join(OUTPUT_ROOT_DIR, csv_filename)

            print(f"\n{'='*60}")
            print(f"正在处理文件：{filename}")
            print(f"输出CSV文件：{csv_filename}")
            print(f"{'='*60}")

            file_data = process_sample(file_path)
            if not file_data:
                print(f"文件 {filename} 无有效样本，跳过")
                continue

            print(f"文件 {filename} 共加载 {len(file_data)} 个样本")
            print("开始推理...")

            results = []

            for idx, sample in enumerate(file_data):
                prompt = generate_prompt(
                    sample["history_context"],
                    sample["current_block"],
                    sample["block_index"]
                )

                # ===== 重试机制 =====
                response = None
                max_retries = 3
                retry_delay = 5

                for attempt in range(max_retries):
                    try:
                        response = agent.input(prompt).start()
                    except Exception:
                        # Agently 子线程异常，直接忽略
                        pass

                    if isinstance(response, str) and response.strip():
                        # 成功拿到结果，跳出重试循环
                        break

                    if attempt < max_retries - 1:
                        print(
                            f"[重试] Block {sample['block_index']} "
                            f"第 {attempt + 1}/{max_retries} 次失败，"
                            f"{retry_delay}s 后重试"
                        )
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        # 3次重试都失败
                        print(
                            f"[警告] Block {sample['block_index']} "
                            f"3 次重试均失败，按默认 HighDanger=False 处理"
                        )

                # ===== 处理重试失败的情况 =====
                if not isinstance(response, str) or not response.strip():
                    results.append({
                        "block_range": sample["block_range"],
                        "HighDanger": False  # 默认设为 False
                    })
                    time.sleep(10)  # 长时间等待，避免连续失败
                    continue

                # ===== 打印模型原始返回 =====
                print(
                    f"\n[进度 {idx + 1}/{len(file_data)}] "
                    f"Block {sample['block_index']} ({sample['block_range']}) 模型原始返回:"
                )
                print("-" * 60)
                print(response)
                print("-" * 60)

                # ===== 解析结果 =====
                try:
                    result_json = extract_json_from_text(response) or {
                        "HighDanger": None
                    }
                except TypeError:
                    result_json = {"HighDanger": None}

                results.append({
                    "block_range": sample["block_range"],
                    "HighDanger": result_json.get("HighDanger")
                })

            # 保存 CSV
            save_results_to_csv(results, output_file_path)
            print(f"\n文件 {filename} 处理完成，结果已保存至：{output_file_path}")

    print("\n所有文件处理完毕！")

if __name__ == "__main__":
    main()
