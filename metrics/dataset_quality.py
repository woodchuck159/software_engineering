from datasets import load_dataset
import pandas as pd
from typing import Dict, Any, List


def evaluate_dataset_quality(dataset_name: str, split: str = "train") -> Dict[str, Any]:
    """
    Evaluate quality of a Hugging Face dataset using Pandas checks
    
    Args:
        dataset_name (str): Hugging Face dataset name (e.g., "imdb").
        split (str): Which split to evaluate ("train", "test", etc.).
    
    Returns:
        Dict[str, Any]: Quality metrics and failed checks.
    """
    # 1. Load dataset into Pandas
    hf_dataset = load_dataset(dataset_name, split=split)
    df = hf_dataset.to_pandas()

    results: Dict[str, Any] = {}
    failed_checks: List[str] = []
    passed_checks: List[str] = []

    # 2. Define basic quality checks
    checks = {
        "row_count > 0": len(df) > 0,
        "no_missing_values": df.isnull().sum().sum() == 0,
        "no_duplicates": not df.duplicated().any(),
    }

    if "text" in df.columns:
        checks["no_empty_text"] = (df["text"].str.strip() != "").all()

    if "label" in df.columns:
        value_counts = df["label"].value_counts(normalize=True)
        checks["balanced_labels"] = (value_counts.min() >= 0.05)

    # 3. Run checks
    for check, passed in checks.items():
        if passed:
            passed_checks.append(check)
        else:
            failed_checks.append(check)

    # 4. Build results
    results["row_count"] = len(df)
    results["passed_checks"] = passed_checks
    results["failed_checks"] = failed_checks
    dataset_quality: float = len(passed_checks) / len(checks)

    return dataset_quality


if __name__ == "__main__":
    results = evaluate_dataset_quality("imdb", "train")
    print("Dataset Quality Results:", results)
