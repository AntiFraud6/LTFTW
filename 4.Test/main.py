# main.py
import os
import glob
import traceback
import warnings
import config.settings as cfg
from utils.block_processor import process_sample
from models.model_loader import load_model
from models.model_infer import ModelInferencer
import csv
import torch
import torch.distributed as dist


# 注意：虽然不用 DDP 包装模型了，但保留 dist 用于数据切分和进程管理


def setup_logging():
    """设置日志"""
    os.makedirs(os.path.dirname(cfg.LOG_FILE), exist_ok=True)


def process_all_samples():
    """处理所有样本"""
    local_rank = int(os.environ.get('LOCAL_RANK', 0))
    dist.init_process_group(backend='nccl')
    torch.cuda.set_device(local_rank)
    rank = dist.get_rank()
    world_size = dist.get_world_size()

    try:
        # 设置日志 (仅主进程执行)
        if rank == 0:
            setup_logging()
            os.makedirs(cfg.RESULTS_DIR, exist_ok=True)

        dist.barrier()  # 等待所有进程准备就绪

        # 加载模型
        if rank == 0:
            print("=" * 50)
            print("开始加载模型...")

        # 1. 加载模型 (Base 或 Peft)
        model, tokenizer = load_model()

        # 2. 将模型移至当前进程对应的 GPU
        model = model.to(local_rank)

        # 3. (可选) 如果是 PeftModel 且显存足够，可以合并权重以加速推理
        # if cfg.CHECKPOINT_PATH and hasattr(model, "merge_and_unload"):
        #     if rank == 0:
        #         print("正在合并 LoRA 权重以加速推理...")
        #     model = model.merge_and_unload()

        # 4. 初始化推理器 (不再传入 DDP 模型)
        inferencer = ModelInferencer(model, tokenizer)

        if rank == 0:
            print("模型加载完成！")
            print("=" * 50)

        # 获取所有jsonl文件
        jsonl_files = glob.glob(os.path.join(cfg.DATA_DIR, "*.jsonl"))

        # 数据切分：每个进程只处理自己的那部分文件
        jsonl_files = jsonl_files[rank::world_size]

        if not jsonl_files:
            if rank == 0:
                print(f"在 {cfg.DATA_DIR} 目录中未找到jsonl文件")
            return

        if rank == 0:
            print(f"共发现 {len(jsonl_files)} 个文件分配给当前进程处理")

        for file_idx, jsonl_file in enumerate(jsonl_files, 1):

            # 提前计算输出路径，以便在异常时能够精准删除残缺文件
            base_name = os.path.splitext(os.path.basename(jsonl_file))[0]
            output_file = os.path.join(cfg.RESULTS_DIR, f"{base_name}_analysis.csv")

            try:
                # 仅主进程打印进度
                if rank == 0:
                    print(f"\n处理文件 {file_idx}/{len(jsonl_files)}: {os.path.basename(jsonl_file)}")

                # 预处理样本，创建blocks
                blocks_data = process_sample(
                    jsonl_file,
                    block_size=cfg.BLOCK_SIZE,
                    history_blocks=cfg.HISTORY_BLOCKS
                )

                if not blocks_data:
                    if rank == 0:
                        print(f"警告: 文件 {jsonl_file} 中没有足够的对话块")
                    continue  

                if rank == 0:
                    print(f"共{len(blocks_data)} 个需要分析的block")

                # 初始化上一个block的数据
                last_block_data = {
                    "L_f": 0.1,
                    "L_n": 0.1,
                    "L_t": 0.1,
                    "L_s": 0.1
                }

                first_block = True
                for i, block_data in enumerate(blocks_data):
                    if rank == 0:
                        print(f"分析block {block_data['block_index']}")

                    # 调用模型推理
                    result = inferencer.infer(
                        block_data["history_context"],
                        block_data["current_block"],
                        block_data["block_index"],
                        last_block_data
                    )

                    last_block_data = {
                        "L_f": result.get("L_f", 0.5),
                        "L_n": result.get("L_n", 0.5),
                        "L_t": result.get("L_t", 0.5),
                        "L_s": result.get("L_s", 0.5)
                    }

                    # 实时写入CSV
                    if first_block:
                        os.makedirs(os.path.dirname(output_file), exist_ok=True)
                        fieldnames = list(result.keys())
                        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerow(result)
                        first_block = False
                    else:
                        with open(output_file, 'a', encoding='utf-8-sig', newline='') as f:
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writerow(result)

                    if rank == 0:
                        print(f"  block {block_data['block_index']} 分析完成并已保存")

            except Exception as e:
                print(f"[Rank {rank}] 处理文件 {jsonl_file} 时出错: {str(e)}")
                traceback.print_exc()

                if os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                        print(f"[Rank {rank}] 已清理残缺文件: {output_file}")
                    except OSError as oe:
                        print(f"[Rank {rank}] 清理文件失败: {oe}")
                print(f"[Rank {rank}] 跳过当前文件，继续处理后续文件...")
                continue

        if rank == 0:
            print("\n" + "=" * 50)
            print("所有文件处理完成！")
            print(f"结果保存在: {cfg.RESULTS_DIR}")
            print("=" * 50)

    finally:
        dist.destroy_process_group()


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    process_all_samples()

