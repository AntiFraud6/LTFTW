# main.py
import os
import asyncio
from utils.block_processor import process_sample
from utils.annotator import annotate_blocks_async
from utils.csv_handler import batch_save_samples
from agents.agent_factory import AgentFactory


async def process_single_file(file_path: str, output_dir: str):
    """异步处理单个文件"""
    file_name = os.path.basename(file_path)
    print(f"\n正在处理: {file_name}")

    try:
        # 步骤1: 分割Block并准备数据
        block_data_list = await asyncio.to_thread(process_sample, file_path)
        print(f"成功分割出 {len(block_data_list)} 个Block")

        # 步骤2: 为当前文件创建专属代理
        agent = AgentFactory.create_agent('reasoner')

        # 步骤3: 异步标注blocks
        annotated_blocks = await annotate_blocks_async(
            block_data_list,
            agent,
            max_concurrent=1
        )

        # 步骤4: 保存当前样本
        current_sample_data = {file_path: annotated_blocks}
        await asyncio.to_thread(batch_save_samples, current_sample_data, output_dir)

        print(f"完成处理并保存: {file_name} → {len(annotated_blocks)}个Block")
        return file_name, True
    except Exception as e:
        print(f"处理失败 {file_name}: {e}")
        return file_name, False


async def main(max_concurrent_files: int = 1):
    """异步主函数，控制文件级并发数"""
    input_dir = r""
    output_dir = r""

    # 收集所有jsonl文件
    jsonl_files = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".jsonl"):
            file_path = os.path.join(input_dir, file_name)
            jsonl_files.append(file_path)

    # 创建信号量控制并发文件数
    semaphore = asyncio.Semaphore(max_concurrent_files)

    async def process_file_with_limit(file_path: str):
        """带并发限制的文件处理"""
        async with semaphore:
            return await process_single_file(file_path, output_dir)

    # 创建所有任务
    tasks = [process_file_with_limit(file_path) for file_path in jsonl_files]

    # 并行执行所有任务（但受信号量限制）
    results = await asyncio.gather(*tasks)

    # 统计结果
    success_count = sum(1 for _, success in results if success)
    print(f"\n处理完成！成功: {success_count}/{len(results)} 个文件")
    print(f"并发限制: {max_concurrent_files} 个文件同时处理")
    print(f"结果已保存到: {output_dir}")


if __name__ == "__main__":
    # 在这里指定并发数
    asyncio.run(main(max_concurrent_files=10))






