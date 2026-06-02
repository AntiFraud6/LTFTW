# main.py
import pandas as pd
import os
import traceback
import asyncio
import concurrent.futures
from utils.save import save_dialogue_to_csv
from config.settings import SYSTEM_CONFIG
from config.prompt import get_stage_configs
from dialogue.Discriminator import detect_fraud_async
from dialogue.Generator import generate_dialogue_chunk_async
from agents.create import AgentFactory

CSV_PATH = SYSTEM_CONFIG['csv_path']
MAX_ATTEMPTS = SYSTEM_CONFIG['max_attempts']
OUTPUT_DIR = SYSTEM_CONFIG['output_dir']
MAX_WORKERS = SYSTEM_CONFIG.get('max_workers', 20)  # 添加并行工作进程数配置


async def process_background(idx, row, agent_factory):
    """处理单个背景的异步函数"""
    background_value = row.get('文章正文内容', '')

    if pd.isna(background_value) or background_value is None:
        print(f"跳过第{idx}行，无背景内容")
        return None

    background = str(background_value).strip()
    if not background:
        print(f"跳过第{idx}行，背景内容为空")
        return None

    print(f"进程 {os.getpid()} 开始处理背景 {idx + 1}")

    try:
        # 为当前进程创建独立的agent实例
        Gemini = agent_factory.create_agent('Gemini')
        v3 = agent_factory.create_agent('DeepSeekv3')

        STAGE_CONFIGS = get_stage_configs()
        dialogue_history = []
        global_round_counter = 0

        for stage_idx, stage_config in enumerate(STAGE_CONFIGS):
            stage_name = stage_config['name']
            stage_rounds = stage_config['total_rounds']
            chunk_size = stage_config['chunk_size']

            print(f"进程 {os.getpid()} - 开始阶段 {stage_idx + 1}/{len(STAGE_CONFIGS)}: {stage_name}")
            print(f"进程 {os.getpid()} - 目标轮数: {stage_rounds}, 分批大小: {chunk_size}")
            print(f"进程 {os.getpid()} - 当前全局轮数: {global_round_counter}")

            stage_generated = 0
            feedback = ""

            # 阶段内分批生成
            while stage_generated < stage_rounds:
                current_chunk_size = min(chunk_size, stage_rounds - stage_generated)
                start_round_global = global_round_counter + 1
                end_round_global = global_round_counter + current_chunk_size
                print(f"进程 {os.getpid()} - 生成第{start_round_global}-{end_round_global}轮对话...")

                attempts = 0
                chunk_accepted = False

                while attempts < MAX_ATTEMPTS and not chunk_accepted:
                    attempts += 1
                    print(f"进程 {os.getpid()} - 尝试欺骗判别器次数： {attempts}/{MAX_ATTEMPTS}")

                    # 使用异步生成
                    current_chunk = await generate_dialogue_chunk_async(
                        Gemini,  # 传入进程特定的agent
                        background,
                        dialogue_history[-10:] if dialogue_history else [],
                        feedback,
                        global_round_counter,
                        current_chunk_size,
                        stage_config['prompt_template'],
                        stage_config['name']
                    )

                    # 异步检测
                    detection_result = await detect_fraud_async(
                        v3,  # 传入进程特定的agent
                        current_chunk
                    )
                    print(f"进程 {os.getpid()} - 检测结果: {detection_result['detection_status']}, "
                          f"风险分数: {detection_result['risk_score']}")

                    if detection_result['risk_score'] < 0.9:
                        print(f"进程 {os.getpid()} - 检测通过")
                        dialogue_history.extend(current_chunk)
                        stage_generated += current_chunk_size
                        global_round_counter += current_chunk_size
                        chunk_accepted = True
                        feedback = ""
                    else:
                        print(f"进程 {os.getpid()} - 检测未通过")
                        feedback = detection_result.get('refinement_suggestions',
                                                        "对话特征明显，请更隐蔽地表达。")

                        if attempts == MAX_ATTEMPTS:
                            print(f"进程 {os.getpid()} - 达到最大尝试次数，使用最后一次生成的对话")
                            dialogue_history.extend(current_chunk)
                            stage_generated += current_chunk_size
                            global_round_counter += current_chunk_size
                            chunk_accepted = True
                            feedback = ""

                    await asyncio.sleep(1)  # 异步sleep

            print(f"进程 {os.getpid()} - 阶段 {stage_name} 完成，生成 {stage_rounds} 轮对话，"
                  f"累计全局轮数: {global_round_counter}")

        print(f"进程 {os.getpid()} - 背景 {idx + 1} 完成，共生成 {len(dialogue_history)} 轮对话")

        # 保存结果
        save_dialogue_to_csv(dialogue_history, idx, OUTPUT_DIR)
        return dialogue_history

    except Exception as e:
        print(f"进程 {os.getpid()} - 处理背景 {idx + 1} 时发生错误: {e}")
        print(f"进程 {os.getpid()} - 错误详情: {traceback.format_exc()}")
        return None


def process_background_sync(idx, row):
    """处理单个背景的同步包装函数，用于进程池"""
    # 为每个进程创建独立的agent工厂
    agent_factory = AgentFactory()

    # 运行异步任务
    return asyncio.run(process_background(idx, row, agent_factory))


async def main_async():
    """异步主函数"""
    if not os.path.exists(CSV_PATH):
        print(f"CSV文件不存在: {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH, encoding='utf-8')

    # 使用进程池并行处理
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 准备任务参数
        tasks = []
        for idx, row in df.iterrows():
            if idx < 1:#跳过背景以支持断点。
                continue
            tasks.append((idx, row))

        # 提交所有任务
        future_to_idx = {}
        for idx, row in tasks:
            future = executor.submit(process_background_sync, idx, row)
            future_to_idx[future] = idx

        # 收集结果
        results = []
        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                result = future.result()
                if result is not None:
                    results.append((idx, result))
                    print(f"背景 {idx + 1} 处理完成")
            except Exception as e:
                print(f"处理背景 {idx + 1} 时发生未捕获的异常: {e}")

    print(f"所有处理完成，共处理 {len(results)} 个背景")


def main():
    """主函数 - 同步入口"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

