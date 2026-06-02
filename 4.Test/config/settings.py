# 模型配置

MODEL_NAME = "/n96pfs/home/ysn96pg0001/model/qwen3-8b-merged"
CHECKPOINT_PATH = ""  # 可设置为模型检查点路径
MAX_TOKENS = 64*1024
MAX_RETRIES = 30
TEMPERATURE = 1

# 路径配置
DATA_DIR = "/n96pfs/home/ysn96pg0001/SCI/Data/0.Dialogue-Test"
#输入路径 存放对话的jsonl文件
RESULTS_DIR = "/n96pfs/home/ysn96pg0001/SCI/Result/BlockSize/15"
#输出路径 输出pred预测的csv文件
LOG_FILE = "/n96pfs/home/ysn96pg0001/SCI/Log2"

# Block配置
BLOCK_SIZE = 15
HISTORY_BLOCKS = 2
