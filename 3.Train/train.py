import os
import warnings

warnings.filterwarnings("ignore")

import torch
import torch.distributed as dist
import psutil


def print_memory_usage(step_name):
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"[Memory Usage] {step_name}: {memory_mb:.2f} MB")


def setup_ddp():
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    world_size = int(os.environ.get("WORLD_SIZE", 1))

    print(f"初始化分布式环境: local_rank={local_rank}, world_size={world_size}")
    torch.cuda.set_device(local_rank)

    if not dist.is_initialized():
        dist.init_process_group(
            backend="nccl",
            init_method="env://",
            rank=local_rank,
            world_size=world_size,
            device_id=local_rank
        )

    if local_rank == 0:
        print(f"DDP初始化完成, 后端: {dist.get_backend()}")


def cleanup_ddp():
    if dist.is_initialized():
        dist.destroy_process_group()


def main():
    setup_ddp()

    if dist.get_rank() == 0:
        print_memory_usage("训练开始前")

    from trainers.sft_trainer import SFTTrainer
    trainer = SFTTrainer()

    if dist.get_rank() == 0:
        print_memory_usage("模型加载后")

    trainer.train()

    if dist.get_rank() == 0:
        print_memory_usage("训练完成后")

    cleanup_ddp()


if __name__ == "__main__":
    main()
