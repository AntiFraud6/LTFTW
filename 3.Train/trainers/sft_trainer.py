import warnings

warnings.filterwarnings("ignore")

import os
import torch
import torch.distributed as dist
from torch.utils.data import Dataset as TorchDataset
from transformers import Trainer, TrainingArguments, DataCollatorForSeq2Seq
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from config.settings import *
from utils.data_utils import load_jsonl, preprocess
from models.model_loader import load_model


class JsonlDataset(TorchDataset):
    def __init__(self, data, tokenizer, max_len):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        try:
            return preprocess(self.data[idx], self.tokenizer, self.max_len)
        except Exception as e:
            print(f"数据预处理错误 (样本 {idx}): {e}")
            return {
                "input_ids": [self.tokenizer.pad_token_id] * 50,
                "attention_mask": [1] * 50,
                "labels": [-100] * 50
            }


class SFTTrainer:
    def __init__(self):
        self.model, self.tokenizer = load_model()
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if not isinstance(self.model, PeftModel):
            cfg = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=LORA_R,
                lora_alpha=LORA_ALPHA,
                lora_dropout=LORA_DROPOUT,
                target_modules=LORA_TARGET_MODULES,
                bias="none"
            )
            self.model = get_peft_model(self.model, cfg)
            # 现代 peft 推荐使用 .print_trainable_parameters() 或手动打印
            self.model.print_trainable_parameters()

    def train(self):
        rank = dist.get_rank()
        world_size = dist.get_world_size()

        if rank == 0:
            print(f"Rank {rank} 开始加载数据...")

        raw_data = load_jsonl(DATA_PATH)
        val_raw_data = load_jsonl(VAL_DATA_PATH)

        train_dataset = JsonlDataset(raw_data, self.tokenizer, MAX_SEQ_LENGTH)
        val_dataset = JsonlDataset(val_raw_data, self.tokenizer, MAX_SEQ_LENGTH)

        # Trainer 原生已完美支持 DDP 和 DistributedSampler，无需手动覆写 DataLoader
        args = TrainingArguments(
            output_dir=OUTPUT_DIR,
            learning_rate=LEARNING_RATE,
            num_train_epochs=NUM_EPOCHS,
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=GRAD_ACCUM_STEPS,
            logging_steps=20,
            save_strategy="steps",
            save_steps=10,
            save_total_limit=100,
            eval_strategy="steps",
            eval_steps=10,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            bf16=True,
            bf16_full_eval=True,
            ddp_find_unused_parameters=True,
            gradient_checkpointing=True,
            gradient_checkpointing_kwargs={"use_reentrant": False},
            report_to="none",
            dataloader_num_workers=0,
            remove_unused_columns=False,
            logging_dir=f"{OUTPUT_DIR}/logs",
            disable_tqdm=(rank != 0)  # 只在主进程显示进度条
        )

        from transformers import EarlyStoppingCallback

        trainer = Trainer(
            model=self.model,
            args=args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
            data_collator=DataCollatorForSeq2Seq(
                tokenizer=self.tokenizer,
                padding=True,
                max_length=MAX_SEQ_LENGTH
            ),
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )

        dist.barrier()

        if rank == 0:
            print("开始训练")

        try:
            trainer.train()

            if rank == 0:
                trainer.save_model(f"{OUTPUT_DIR}/final")
                print(f"训练完成，模型保存至: {OUTPUT_DIR}/final")

        except Exception as e:
            print(f"Rank {rank} 训练过程中出现错误: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            raise
