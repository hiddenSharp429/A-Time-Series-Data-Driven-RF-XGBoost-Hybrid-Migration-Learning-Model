import pandas as pd
from models.feature_engineering.feature_selector import FeatureSelector
from models.sampling.balanced_sampler import BalancedSampler
from config import FAULT_DESCRIPTIONS
from utils.data_loader import DataLoader
from utils.data_process import split_train_test_datasets, remove_irrelevant_features


def select_and_save_features(production_line_code, fault_code, threshold, negative_positive_ratio, balance=True, temporal=True):
    """Select important features for a specific fault code and save results

    Args:
        production_line_code (int): Production line code
        fault_code (int): Fault code
        threshold (float): Threshold for feature selection
        negative_positive_ratio (float): Ratio for balanced sampling
        balance (bool): Balance dataset
        temporal (bool): Use Temporal data
    """
    # Load data
    data_loader = DataLoader()
    data = data_loader.prepare_data(production_line_code, temporal)
    data['label'] = (data[FAULT_DESCRIPTIONS[fault_code]] == fault_code)

    train_data, test_data = split_train_test_datasets(data, fault_code)
    train_data, _ = remove_irrelevant_features(train_data)
    test_data, _ = remove_irrelevant_features(test_data)

    y_train = train_data['label']
    x_train = train_data.drop('label', axis=1)
    y_test = test_data['label']
    x_test = test_data.drop('label', axis=1)

    if balance:
        sampler = BalancedSampler(negative_positive_ratio=negative_positive_ratio)
        x_train, x_test, y_train, y_test = sampler.balance_dataset(x_train, x_test, y_train, y_test)

    train_data = pd.concat([x_train, y_train], axis=1)
    test_data = pd.concat([x_test, y_test], axis=1)

    feature_selector = FeatureSelector()
    x_train_selected, x_test_selected = feature_selector.select_important_features(
        train_data=train_data,
        test_data=test_data,
        fault_code=fault_code,
        threshold=threshold,
        model_exist=False
    )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Select important features for fault prediction')
    parser.add_argument('--production_line', type=int, required=True, help='Production line code')
    parser.add_argument('--fault_code', type=int, required=True, help='Fault code')


    parser.add_argument('--no-temporal', action='store_false', dest='temporal', help='Do not use Temporal data')

    parser.add_argument('--ratio', type=float, default=10.0, help='Negative/positive ratio for balanced sampling')
    parser.add_argument('--threshold', type=float, default=0.9, help='Threshold for feature selection')
    parser.add_argument('--no-balance', action='store_false', dest='balance', help='Do not balance dataset')


    parser.set_defaults(temporal=True, balance=True)

    # Parse command line arguments
    args = parser.parse_args()

    # Call function with parsed arguments
    select_and_save_features(args.production_line, args.fault_code, args.threshold, args.ratio, args.balance, args.temporal)