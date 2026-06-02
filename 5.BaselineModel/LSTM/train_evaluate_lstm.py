import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd
import random
import numpy as np

from config import *
from data_loader import prepare_data, load_specific_file
from vectorizer import get_embeddings
from lstm_model import TextDataset, LSTMClassifier, train_model

def main():
    # 设置多GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = CUDA_VISIBLE_DEVICES
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # 1. 加载数据
    train_df, test_df = prepare_data(TRAIN_DIR, TEST_DIR)
    
    # 2. 向量化文本
    print("\nVectorizing training data...")
    train_texts = train_df['text'].tolist()
    train_labels = train_df['label'].tolist()
    train_embeddings = get_embeddings(train_texts, batch_size=BATCH_SIZE)
    
    # 3. 对训练集进行正例反例均衡化
    X_train_pos = [train_embeddings[i] for i, label in enumerate(train_labels) if label == 1]
    y_train_pos = [1] * len(X_train_pos)
    X_train_neg = [train_embeddings[i] for i, label in enumerate(train_labels) if label == 0]
    y_train_neg = [0] * len(X_train_neg)
    
    min_count = min(len(X_train_pos), len(X_train_neg))
    
    if len(X_train_pos) > min_count:
        indices = random.sample(range(len(X_train_pos)), min_count)
        X_train_pos = [X_train_pos[i] for i in indices]
        y_train_pos = [1] * min_count
    
    if len(X_train_neg) > min_count:
        indices = random.sample(range(len(X_train_neg)), min_count)
        X_train_neg = [X_train_neg[i] for i in indices]
        y_train_neg = [0] * min_count
    
    X_train = X_train_pos + X_train_neg
    y_train = y_train_pos + y_train_neg
    
    combined = list(zip(X_train, y_train))
    random.shuffle(combined)
    X_train, y_train = zip(*combined)
    X_train, y_train = list(X_train), list(y_train)
    
    print(f"After balancing: {len(X_train)} samples ({sum(y_train)} positive, {len(y_train)-sum(y_train)} negative)")
    
    # 4. 重塑数据
    X_train = np.array(X_train).reshape(len(X_train), 1, -1)
    
    # 5. 划分训练集和验证集
    X_train_split, X_val, y_train_split, y_val = train_test_split(
        X_train, y_train, 
        test_size=0.2, 
        random_state=42,
        stratify=y_train
    )
    
    # 6. 创建数据集和数据加载器
    train_dataset = TextDataset(X_train_split, y_train_split)
    val_dataset = TextDataset(X_val, y_val)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    # 7. 初始化模型
    input_dim = X_train.shape[2]
    output_dim = 2
    
    model = LSTMClassifier(
        input_dim=input_dim,
        hidden_dim=HIDDEN_DIM,
        output_dim=output_dim,
        num_layers=NUM_LAYERS
    )
    
    # 使用多GPU训练
    if torch.cuda.device_count() > 1:
        print(f"Using {torch.cuda.device_count()} GPUs!")
        model = nn.DataParallel(model)
    
    # 8. 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # 9. 训练模型
    print("\nStarting training...")
    train_model(
        model, train_loader, val_loader, 
        criterion, optimizer, device, 
        epochs=EPOCHS
    )
    
    # 10. 加载最佳模型并在测试集上评估
    print("\nEvaluating on test set...")
    
    # 加载权重
    state_dict = torch.load('best_lstm_model.pth')
    
    # 移除 'module.' 前缀（如果存在）
    from collections import OrderedDict
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        if k.startswith('module.'):
            name = k[7:]  # 移除 'module.' 前缀
        else:
            name = k
        new_state_dict[name] = v
    
    # 加载权重
    if isinstance(model, nn.DataParallel):
        model.module.load_state_dict(new_state_dict)
    else:
        model.load_state_dict(new_state_dict)
    
    model.eval()
    
    # 11. 按文件处理测试数据
    test_files = [f for f in os.listdir(TEST_DIR) if f.endswith('.jsonl')]
    
    for test_file in test_files:
        print(f"\nProcessing test file: {test_file}")
        test_filepath = os.path.join(TEST_DIR, test_file)
        
        df_test = load_specific_file(test_filepath)
        X_test_texts = df_test["text"].tolist()
        y_test = df_test["label"].tolist()
        
        X_test_embeddings = get_embeddings(X_test_texts, batch_size=BATCH_SIZE)
        X_test_embeddings = np.array(X_test_embeddings).reshape(len(X_test_embeddings), 1, -1)
        
        X_test_tensor = torch.FloatTensor(X_test_embeddings).to(device)
        
        with torch.no_grad():
            outputs = model(X_test_tensor)
            _, y_pred = torch.max(outputs.data, 1)
            y_pred = y_pred.cpu().numpy()
        
        result_df = pd.DataFrame({
            "true_label": y_test,
            "predicted_label": y_pred,
            "true_bool": [bool(x) for x in y_test],
            "pred_bool": [bool(x) for x in y_pred]
        })
        
        base_filename = os.path.splitext(test_file)[0]
        result_path = os.path.join(OUTPUT_DIR, f"{base_filename}_LSTM_predictions.csv")
        result_df.to_csv(result_path, index=False)
        print(f"  {test_file} predictions saved to {result_path}")
        
        print(f"  Classification Report for LSTM on {test_file}:")
        print(classification_report(y_test, y_pred, digits=4))

if __name__ == "__main__":
    main()
