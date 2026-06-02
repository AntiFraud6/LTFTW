#main.py
from ConvertClean.convert import process_directory
if __name__ == "__main__":
    INPUT_DIRECTORY = r""
    #输入路径：模型返回的csv文件
    OUTPUT_DIRECTORY = r""
    #输出路径：经过数据处理后的文件

    process_directory(INPUT_DIRECTORY, OUTPUT_DIRECTORY)