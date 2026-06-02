# 🕵️‍♂️ 诈骗对话生成与分析流水线

一站式工具链：从诈骗对话生成、数据清洗、模型标注、训练推理，到最终指标计算与敏感性分析。  
各模块独立运行，配置灵活，助你快速复现实验。

---

## 📑 目录

- [0. AntiGenerate – 对话生成](#0-antigenerate--对话生成)
- [1. DataProcess – 数据清洗](#1-dataprocess--数据清洗)
- [2. R1CoTGenerate – 对话标注](#2-r1cotgenerate--对话标注)
- [3. Trian – 模型训练](#3-trian--模型训练)
- [4. Test – 模型推理](#4-test--模型推理)
- [5. BaselineModel – 基线二分类](#5-baselinemodel--基线二分类)
  - [5.1 TraditionalML](#51-traditionalml)
  - [5.2 LSTM](#52-lstm)
  - [5.3 LLMs](#53-llms)
- [6. F1Compute – 指标计算](#6-f1compute--指标计算)
  - [6.1 RTCompute](#61-rtcompute)
  - [6.2 HighDangerLabel](#62-highdangerlabel)
  - [6.3 ComputeF1csvFile](#63-computef1csvfile)
  - [6.4 Metrics / Metrics2](#64-metrics--metrics2)
- [7. SensitivityAnalysis – 敏感性分析](#7-sensitivityanalysis--敏感性分析)
- [MakeLabel.py – 高危标签添加](#makelabelpy--高危标签添加)

---

## 0. AntiGenerate – 对话生成

🎯 **功能**：根据背景新闻生成诈骗对话。

### ⚙️ 配置 `config/settings.py`

- 设置 **DeepSeek (fast-thinking)** 的 API
- 设置 **Gemini / DouBao / GPT** 的 API（统一命名为 `Gemini`，底层已替换为对应模型）
- 设置 `output_dir`：CSV 对话文件输出路径
- 设置 `csv_path`：诈骗新闻报道背景文件路径

🚀 **启动**：执行 `main.py` 即可。

---

## 1. DataProcess – 数据清洗

🧹 **功能**：处理模型返回的原始数据（清洗、格式转换等）。

### ⚙️ 配置 `main.py`

- 设置 `INPUT_DIRECTORY`
- 设置 `OUTPUT_DIRECTORY`

🚀 修改路径后直接运行 `main.py`。

---

## 2. R1CoTGenerate – 对话标注

🏷️ **功能**：使用模型对生成的对话进行序列标注。

### ⚙️ 配置

- `config/settings.py`：设置 **DeepSeek (slow-thinking)** API
- `utils/block_processor.py`：设置 `BlockSize` 
  *(实验默认 `BlockSize=10`，敏感性分析中使用 `5` 和 `15`)*

### 🚀 运行 `main.py`

- 设置 `input_dir`：经 **DataProcess** 处理后的诈骗对话 JSONL 文件  
- 设置 `output_dir`：标注结果输出目录（CSV）
- 并发控制：`asyncio.run(main(max_concurrent_files=x))` 按电脑配置调整并发数

---

## 3. Trian – 模型训练

🏋️ **功能**：基于标注数据微调模型。

### ⚙️ 配置 `config/settings.py`

- `MODEL_NAME`：基础模型路径（通常为本地路径）
- `CHECKPOINT_PATH`：为空则直接使用 base model；否则为 **base + 第一阶段 Checkpoint**（即在微调阶段1基础上进行阶段2）
- `DATA_PATH`：训练数据路径（Dataset 已提供）
- `OUTPUT_DIR`：Checkpoint 输出路径
- `VAL_DATA_PATH`：验证数据路径（用于早停，Dataset 已提供）

🚀 **运行命令**：

```bash
torchrun --nproc_per_node=4 --master_port=29500 train.py
```



---

## 4. Test – 模型推理

🔍 **功能**：加载模型进行推理，输出预测结果（Pred）。

### ⚙️ 配置 `config/settings.py`

- `MODEL_NAME`：基础模型路径
- `CHECKPOINT_PATH`：为空则直接使用 base model；否则为微调后的模型路径
- `DATA_DIR`：输入数据目录（大模型生成的对话 Test 集，JSONL 格式）
- `RESULTS_DIR`：预测结果输出目录
- `BlockSize` *(同前，实验默认 `10`，敏感性分析 `5`/`15`)*

---

## 5. BaselineModel – 基线二分类

📊 **说明**：不依赖 LTFTW 框架，仅进行简单的高危 / 非高危二分类。

### 5.1 TraditionalML

🧪 传统机器学习（SVM, KNN, Logistic Regression）。先向量化，再训练 + 推理。

#### ⚙️ `config.py`

- `DATA_DIR`：包含 `HighDanger(true/false)` 的 JSONL 文件（自动划分 train / test）
- `OUTPUT_DIR`：结果输出目录
- `LOCAL_MODEL_DIR`：向量化模型本地路径  
  *模型：`nlp_corom_sentence-embedding_chinese-base`*

最终输出可用于评估的 Pred CSV。

---

### 5.2 LSTM

🧠 LSTM 模型，同样先向量化再训练推理。

#### ⚙️ `config.py`

- `EMBEDDING_MODEL = "damo/nlp_corom_sentence-embedding_chinese-base"`
- `LOCAL_MODEL_DIR`：向量化模型本地路径  
  *同上，使用 `nlp_corom_sentence-embedding_chinese-base`*
- `OUTPUT_DIR`：结果输出目录
- `TRAIN_DIR`：带 `HighDanger` 标签的训练文件
- `TEST_DIR`：带 `HighDanger` 标签的测试文件

最终输出 Pred CSV。

---

### 5.3 LLMs

🤖 直接调用大语言模型进行文本分类，无需额外训练。

#### ⚙️ `config/settings`

- 替换 `api_key` 为实际 API Key
- 设置 `model_name`（待测试模型）
- 设置 `output_dir`（结果输出目录）

#### 🚀 `main.py`

- 设置 `INPUT_DIR`：仅需带 `HighDanger(true/false)` 的 **Test 文件**（LLM 不训练）

最终输出 Pred CSV。

---

## 6. F1Compute – 指标计算

📈 基于步骤4得到的 Pred 信息（如 $L_f$），计算各项评估指标。

### 6.1 RTCompute

🔢 从原始模型返回的 CSV 中计算 R 和 T 值。

- `source_directory`：原始 CSV 文件目录（通常位于 `4.PredDanger\0.InitialData`）
- `target_directory`：输出结果目录（通常位于 `4.PredDanger\1.ProcessedData`）

---

### 6.2 HighDangerLabel

🚨 根据上一步得到的 R、T 值，按预设规则打上高危标签。

- `input_dir`：`4.PredDanger\1.ProcessedData`（含 R、T）
- `output_dir`：`4.PredDanger\2.LabelData`（输出带 Label 的结果）

---

### 6.3 ComputeF1csvFile

📋 生成计算 F1、FPR、MLLT、MAWO 所需的 CSV 文件（pred 与 true 一一对应）。

- `csv_dir`：上一步得到的 Pred 带 Label 的 CSV（`4.PredDanger\2.LabelData`）
- `jsonl_dir`：带 Label 的真值 JSONL 文件（数据中位于 `3.TrueDanger` 目录）
- `output_dir`：最终输出目录（`4.PredDanger\3.Finally`）

---

### 6.4 Metrics / Metrics2

📊 根据最终 CSV 计算指标：
- **Metrics** → 计算 MLLT
- **Metrics2** → 计算 MAWO

---

## 7. SensitivityAnalysis – 敏感性分析

🔬 分析超参数 $\varepsilon$ 和 $R_{th}$ 对结果的影响。

### (0) ComputeRT

将原始 CSV（DeepSeek-Reasoner 原始返回）转换为 JSONL，并重新递归计算 R、T（不依赖之前的 `prev_R`、`prev_T`）。

- 设置 `INPUT_DIR` 为 DeepSeek 标注原始返回路径

---

### (1) AddStage

为新生成的 JSONL 添加 `stage` 字段，便于后续统计 R / T 中位数。

- `dir_a`：(0) 中计算出的带 R、T 的 JSONL 文件
- `dir_b`：之前已包含 `stage` 标注的 JSONL 文件

根据 `dir_b` 的结构为 `dir_a` 补齐 `stage`。

---

### (2) jsonl2csv

将分散的 JSONL 整合到一个 CSV 文件中，记录所有 R、T 信息。

- 设置 `dir_path` 为步骤 (1) 产出的 JSONL 目录

---

### (3) TthRincth

计算 $R_{th}$（$T_{th}$）等阈值。

- `df = pd.read_csv("/Statistics.csv")`  
  *（即步骤 (2) 产出的 CSV 文件）*
- 输出阈值结果到 `output_path`（如 `xxx\result.txt`）

完成后，再通过 **6. F1Compute** 流程计算最终指标。

---

## MakeLabel.py – 高危标签添加

🏷️ 为经过 **2. R1CoTGenerate** 得到的 JSONL 文件添加 `HighDanger(true/false)` 字段，标记是否为高危对话块。  
直接运行该脚本即可完成打标。

---

> 💡 **提示**：所有路径均使用示例目录，请根据实际项目结构修改。  
> 各模块依赖的 API Key、模型路径等请提前在对应配置文件中填写。