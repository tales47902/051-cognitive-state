from typing import List
import sys
import warnings
import time
import pickle

import numpy as np
import pandas as pd
from tqdm import tqdm

from topcoder_cognitive_state.load_data import read_data
from topcoder_cognitive_state.model import Model

warnings.filterwarnings("ignore")


def arrays_to_str_list(arr: np.array) -> List[str]:
    
    result = []
    for i in range(arr.shape[0]):
        tmp = list(arr[i, :])
        tmp = "[" + " ".join([str(s) for s in tmp]) + "]"
        result.append(str(tmp))
    return result


def lists_to_str_list(arr: List[List[str]]) -> List[str]:
   
    result = []
    for tmp in arr:
        tmp = "[" + " ".join(["'" + str(s) + "'" for s in tmp]) + "]"
        result.append(str(tmp))
    return result


def make_predictions_for_test_suite(
    data: pd.DataFrame, test_suite: pd.Series, model: Model
) -> pd.DataFrame:
    
    (
        y_hat_1,
        y_hat_3,
        y_hat_1_label,
        y_hat_3_label,
        most_important_features,
    ) = model.predict(data)

   
    result = pd.DataFrame({})

    result["timestamp"] = data.reset_index()["timestamp"]
    result["test_suite"] = test_suite

    result["predicted_induced_state"] = y_hat_1_label
    result["three_sec_predicted_induced_state"] = y_hat_3_label

    result["predicted_induced_state_confidence"] = arrays_to_str_list(y_hat_1)
    result["three_sec_predicted_induced_state_confidence"] = arrays_to_str_list(y_hat_3)

    result["top_three_features"] = lists_to_str_list(most_important_features)

    result_cols = [
        "timestamp",
        "test_suite",
        "predicted_induced_state",
        "predicted_induced_state_confidence",
        "three_sec_predicted_induced_state",
        "three_sec_predicted_induced_state_confidence",
        "top_three_features",
    ]
    result = result[result_cols]
    return result


def make_predictions(
    data: pd.DataFrame, dummies: pd.DataFrame, model: Model
) -> pd.DataFrame:
    
    t_start = time.time()

 
    tmp = [i[0] for i in data.index]
    test_suites = []
    for t in tmp:
        if t not in test_suites:
            test_suites.append(t)

    result = []
    for test_suite in tqdm(test_suites):
        tmp = make_predictions_for_test_suite(data.loc[test_suite], test_suite, model)
        result.append(tmp)
    result = pd.concat(result, axis=0).reset_index(drop=True)

   
    result = pd.merge(dummies, result, how="left", on=["timestamp", "test_suite"])

   
    result["timestamp"] = (
        pd.to_datetime(result["timestamp"]).apply(lambda x: x.value) / 10**3
    )
    result["timestamp"] = result["timestamp"].astype("int")

    t_end = time.time()
    print(f"Predicions are made. Time: {(t_end-t_start)/60:.2f} minutes")
    return result


def main():
    if len(sys.argv) < 2 or len(sys.argv[1]) == 0:
        print("Testing input file is missing.")
        return 1

    if len(sys.argv) < 3 or len(sys.argv[2]) == 0:
        print("Testing output file is missing.")
        return 1

    print("Testing started.")

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    model_file = sys.argv[3]

    with open(model_file, "rb") as f:
        model = pickle.load(f)


    data, dummies = read_data(input_file)
    result = make_predictions(data, dummies, model)
    result.to_csv(output_file, index=False)
    return 0


if __name__ == "__main__":
    main()
