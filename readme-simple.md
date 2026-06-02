# 0.AntiGenerate

用于根据背景生成诈骗对话

## (1).config/settings.py

设置DeepSeek(fast-thinking)的API

设置Geimini/DouBao/GPT的API(实际上，都取名为Geimini，但没关系，本质已经换成了别的model的API了)

设置output_dir:csv对话文件的输出路径

设置csv_path:诈骗新闻报道背景文件。

执行main.py即可。





# 1.DataProcess

用于处理模型返回的原始数据(进行数据清洗、转换等)

## (1)main.py

设置main.py下的INPUT_DIRECTORY和OUTPUT_DIRECTORY即可运行。







# 2.R1CoTGenerate

用于模型对生成的对话进行标注。

## (1)config/settings.py

设置DeepSeek(slow-thinking)的API

## (2)utils/block_processor.py

设置BlockSize(实验是在BlockSize=10的条件下进行的，参数敏感性分析BlockSize=5,15)

## (3)main.py

设置input_dir与output_dir。

input_dir:生成的诈骗对话，格式为经"DataProcess"代码处理后的jsonl文件。

output_dir：生成的诈骗对话标注，格式为csv文件。

 asyncio.run(main(max_concurrent_files=x))：设置并发数，以适配电脑本身配置。







# 3.Trian

用于训练模型。

## (1)config/settings.py

设置MODEL_NAME：basemodel路径，一般为本地路径。 

设置CHECKPOINT_PATH:为空时，表示直接用basemodel。不空时，为basemode+第一阶段的CheckPoint，即在微调阶段1的基础上进行微调阶段2。

设置DATA_PATH ：训练数据路径。Dataset已提供。
设置OUTPUT_DIR :结果(CheckPoint)输出路径。
设置VAL_DATA_PATH 验证数据路径(用于早停)。Dataset已提供。

运行时执行命令：torchrun --nproc_per_node=4 --master_port=29500 train.py即可。







# 4.Test

模型推理,得出Pred结果。

## (1)config/settings.py

设置MODEL_NAME：basemodel路径，一般为本地路径。
设置CHECKPOINT_PATH:为空时，表示直接用basemodel。不空时，为basemode+CheckPoint，即微调后的模型。

设置DATA_DIR：模型输入数据路径，即为大模型生成的对话的Test的目录（jsonl格式）。
设置RESULTS_DIR：模型pred的结果输出目录。

设置BlockSize(实验是在BlockSize=10的条件下进行的，参数敏感性分析BlockSize=5,15)



# 5.BaselineModel

不用LTFTW框架，只对其进行简单二分类。

## (1)TraditionalML

传统机器学习(SVM KNN Logistic Regression)，先向量化，再进行训练、推理。

### config.py

设置DATA_DIR:带HighDanger(true/false)的jsonl文件(自动划分train test集合)
设置OUTPUT_DIR ：模型结果。

设置LOCAL_MODEL_DIR = "xxxx/nlp_corom_sentence-embedding_chinese-base"。

注意，我们使用的向量化模型是nlp_corom_sentence-embedding_chinese-base。

最终生成可以得出结果的Pred的csv格式文件。

## (2)LSTM

LSTM，先向量化，再进行训练、推理。

### config.py

设置EMBEDDING_MODEL = "damo/nlp_corom_sentence-embedding_chinese-base"
设置LOCAL_MODEL_DIR = "xxx/nlp_corom_sentence-embedding_chinese-base"

同样，我们使用的向量化模型是nlp_corom_sentence-embedding_chinese-base。

设置OUTPUT_DIR ：模型结果。

设置TRAIN_DIR：带HighDanger(true/false)的Train文件。
设置TEST_DIR :带HighDanger(true/false)的Test文件。

最终生成可以得出结果的Pred的csv格式文件。

## (3)LLMs

大语言模型，直接输入文本即可

### config/settings

设置api_key替换为实际API Key
设置model_name需要测试的模型
设置output_dir结果输出目录

最终生成可以得出结果的Pred的csv格式文件。

### main.py

设置INPUT_DIR。与上述不同，LLMs不用训练，所以只设置带HighDanger(true/false)的Test文件即可。





# 6.F1Compute

上述步骤4得到了Pred的$L_f$等信息，下面计算相应指标。

## (1)RTCompute

计算Pred得到的R和T值。

设置source_directory = r"xxx\4.PredDanger\0.InitialData"模型原始返回csv文件，给出的数据中一般保存在4.PredDanger\0.InitialData目录下。
设置target_directory = r"xxx\4.PredDanger\1.ProcessedData"输出结果，给出的数据中一般保存在4.PredDanger\1.ProcessedData目录下。

## (2)HighDangerLabel

上述得到了R和T值，根据所设规则对Pred打Label。

设置input_dir = r"xxx\4.PredDanger\1.ProcessedData"。上述输出结果，有R和T。
设置output_dir = r"xxx\4.PredDanger\2.LabelData"。输出结果，带Label。（根据R和T进行打Label）

## (3)ComputeF1csvFile

生成计算F1 FPR MLLT MAWO的csv格式文件。(含pred/true)

设置csv_dir = r"xxx\4.PredDanger\2.LabelData"为上述得到的pred的带Label的csv文件。
设置jsonl_dir = r"xxxx\3.TrueDanger"为带Label的True的jsonl文件(在所给中数据中，放在3.TrueDanger目录下。)
设置output_dir = r"xxx\4.PredDanger\3.Finally"为最终输出计算F1 FPR MLLT MAWO的csv格式文件。（pred与true一一对应，以便后续计算相应指标。）

## (4)4.Metrics/Metrics2

根据(3)得到的csv文件计算相应指标。Metrics为计算MLLT，Metrics2为计算MAWO。



# 7.SensitivityAnalysis

用于敏感性分析$\varepsilon$和$R_{th}$。同样的，

## (0)ComputeRT

将原始csv文件转换为jsonl文件。csv文件为DeepSeek-Reasoner原始返回，而生成jsonl带R和T（通过代码递归计算，而不是读取之前的prev_R prev_T）。

设置INPUT_DIR 为DeepSeek标注的原始返回，用于计算R和T。

## (1)AddStage

为新的jsonl文件添加stage，以便后续计算R和T的中位数。

设置dir_a为(0)ComputeRT计算得到的R和T的jsonl文件。 
设置dir_b为之前带stage标注的jsonl文件。

根据目录b为目录A添加stage(两者结构相同)。

## (2)jsonl2csv

将jsonl整合到一个csv文件，记录所有的R和T。

设置dir_path为(1)得到的jsonl文件目录结构，最终生成一个csv文件。

## (3)TthRincth

计算$R_{th}$($T_{th}$)等。

设置df = pd.read_csv(
    r"D:\Study\SCI\Dataset\SensitivityAnalysis\Block\Size5\3.TrueDanger\1.Statistics.csv"
)，为(2)得到的csv文件。

最终的$R_{th}$($T_{th}$)输出路径设置为为output_path = r"xxx\result.txt"保存相应的$R_{th}$($T_{th}$)

随后，再通过6计算相应指标即可。



# MakeLabel.py

为经2.R1CoTGenerate得到的jsonl文件添加HighDanger(true/false)，表示是否为高危对话块。