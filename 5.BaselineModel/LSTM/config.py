import os

# 配置参数
EMBEDDING_MODEL = "damo/nlp_corom_sentence-embedding_chinese-base"
LOCAL_MODEL_DIR = "xx/nlp_corom_sentence-embedding_chinese-base"

# 输出目录
OUTPUT_DIR = ""

# 训练参数
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001
HIDDEN_DIM = 128
NUM_LAYERS = 2

# 数据路径
TRAIN_DIR = ''
TEST_DIR = ''

# GPU配置
CUDA_VISIBLE_DEVICES = "0,1,2,3"  # 4张H100

# 创建必要的目录
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
