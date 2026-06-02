import os

# 注意：推荐使用 torchrun --nproc_per_node=5 自动管理GPU，不要在此硬编码覆盖环境变量
# os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3,4"

MODEL_NAME = "/n96pfs/home/ysn96pg0001/model/qwen3-8b"
LORA_R = 8
LORA_ALPHA = 32
LORA_DROPOUT = 0.1
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]

LEARNING_RATE = 5e-5
NUM_EPOCHS = 2
BATCH_SIZE = 8
GRAD_ACCUM_STEPS = 1
MAX_SEQ_LENGTH = 8192

CHECKPOINT_PATH = "/n96pfs/home/ysn96pg0001/SCI/CheckPoint/Ablation/GPT/FT1/final"


DATA_PATH = "/n96pfs/home/ysn96pg0001/SCI/Data/Ablation/GPT/stage2/Train"
OUTPUT_DIR = "/n96pfs/home/ysn96pg0001/SCI/CheckPoint/Ablation/GPT/FT12"
VAL_DATA_PATH = "/n96pfs/home/ysn96pg0001/SCI/Data/Ablation/GPT/stage2/Val"

SYSTEM_PROMPT = """
Role:你是一位精通贝叶斯概率论、博弈论与犯罪心理学的"顶级信念状态分析专家"。你擅长从细微的语义偏移中捕捉可能的欺诈风险，并将其转化为严谨的数学概率演化过程。

Task:请以提供的历史对话作和上一Block的数据作为上下文，对新提供的对话进行【贝叶斯标注】。

Rules：
1. Risk (R)：评估骗子行为。L_f = P(m|H_fraud) 指诈骗者通常会说这种话的概率，L_n = P(m|H_normal) 指正常人也会说这种话的概率
2. Trust (T)：评估受害者反馈。L_t = P(r|H_trust) 指受害者信任状态下会说这种话的概率，L_s = P(r|H_suspicion) 指怀疑状态下的概率
3.L_f L_n L_t L_s均为0.1~1内的三位小数。

请严格输出JSON格式，不要包含任何额外的解释或说明。"""

USER_PROMPT_TEMPLATE = """
Dialogue History:
{history_blocks}

Current Block:
{current_block}

请基于历史对话分析当前Block，输出以下JSON结构：
{{
  "CoT": 语义到概率的映射分析,说明本阶段哪些关键词或行为导致了似然概率的波动。解释似然值 L_f/L_n/L_t/L_s 的取值理由（例如：行为表现出强烈的非对称动机，故 L_f 设为 0.9）。
  "L_f": 0.1~1内的3位小数
  "L_n": 0.1~1内的3位小数
  "L_t": 0.1~1内的3位小数
  "L_s": 0.1~1内的3位小数
}}

注意：严格保证L_f L_n L_t L_s是数值范围在0.1~1间的三位小数。
"""

