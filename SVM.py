import os
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from utils.data_process import data_process
from utils.model_evaluation import evaluate_model
from utils.load_data import get_input_and_prepare_data

def pipeline_failure_prediction():
    pipeline_code, fault_code, fault_description, train_data, test_data = get_input_and_prepare_data()
    
    # 创建结果保存的文件夹
    model_output_folder = 'model/'
    report_output_folder = 'report/'
    os.makedirs(model_output_folder, exist_ok=True)

    # 设置模型名称
    model_name = f'svm{fault_code}_{pipeline_code}'

    y_train = (train_data[f'{fault_description}'] == fault_code)
    y_test = (test_data[f'{fault_description}'] == fault_code)

    # 输入是否需要时序化数据
    need_temporal_features = input("Do you want to load temporal features? (yes/no): ").lower().strip() == 'yes'

    X_train = data_process(train_data, need_temporal_features=need_temporal_features)
    X_test = data_process(test_data, need_temporal_features=need_temporal_features)

    # 标准化特征
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Start training...")
    # 记录开始时间
    start_time = time.time()

    # 初始化 SVM 模型（使用默认参数）
    model = SVC(probability=True, random_state=42)

    # 训练模型
    model.fit(X_train_scaled, y_train)

    # 记录结束时间
    end_time = time.time()
    print(f"SVM模型训练时间: {end_time - start_time:.2f} 秒")

    # 保存模型
    joblib.dump(model, os.path.join(model_output_folder, f"{model_name}.pkl"))

    # 在测试集上评估模型
    y_pred = model.predict(X_test_scaled)
    y_scores = model.predict_proba(X_test_scaled)[:, 1]

    # 使用评估函数
    results = evaluate_model(y_test, y_pred, y_scores, model_name, report_output_folder)

    # 打印一些关键指标
    print(f"Test set accuracy: {results['accuracy']:.4f}")
    print(f"Test set F1 score: {results['f1_score']:.4f}")

    return model, results

if __name__ == "__main__":
    model, results = pipeline_failure_prediction()