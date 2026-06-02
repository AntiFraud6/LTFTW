from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import numpy as np
import torch
from tqdm import tqdm
from config import EMBEDDING_MODEL, LOCAL_MODEL_DIR


def get_embeddings(texts, batch_size=64):
    """
    从本地加载模型 + GPU加速 + 【分批处理】
    """
    model_path = LOCAL_MODEL_DIR

    # 自动检测GPU
    device = "gpu" if torch.cuda.is_available() else "cpu"
    print(f"Loading model from LOCAL PATH | 使用设备: {device.upper()}")

    embed_pipeline = pipeline(
        Tasks.sentence_embedding,
        model=model_path,
        device=device
    )

    print(f"Generating embeddings (分批模式, Batch size: {batch_size})...")

    all_embeddings = []

    # 【核心修改】使用 tqdm 循环，分批处理
    for i in tqdm(range(0, len(texts), batch_size), desc="Processing Batches"):
        batch_texts = texts[i: i + batch_size]
        result = embed_pipeline({"source_sentence": batch_texts})
        all_embeddings.extend(result["text_embedding"])

        # 可选：每步清理一下缓存，防止显存碎片累积
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    return np.array(all_embeddings)