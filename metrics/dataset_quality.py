import os
import time
from typing import Tuple, Dict, Any, List
import pandas as pd
from datasets import load_dataset

def dataset_quality(dataset_name: str, verbosity: int, log_queue) -> Tuple[float, float]:
    """
    Evaluates the quality of a Hugging Face dataset and returns a score and execution time.

    Args:
        dataset_name (str): Hugging Face dataset name (e.g., "imdb").
        verbosity (int): The verbosity level (0=silent, 1=info, 2=debug).
        log_queue (multiprocessing.Queue): The queue for centralized logging.
        split (str): Which split to evaluate ("train", "test", etc.).

    Returns:
        A tuple containing:
        - The dataset quality score (0.0 to 1.0), or -1.0 on error.
        - The total time spent (float).
    """
    start_time = time.perf_counter()
    pid = os.getpid()
    score = 0.0  # Default score for any failure
    split: str = "train"

    try:
        if verbosity >= 1:
            log_queue.put(f"[{pid}] Loading dataset '{dataset_name}' (split: {split})...")
        
        # 1. Load dataset into Pandas
        hf_dataset = load_dataset(dataset_name, split=split)
        df = hf_dataset.to_pandas()

        if verbosity >= 1:
            log_queue.put(f"[{pid}] Dataset '{dataset_name}' loaded with {len(df)} rows. Starting checks...")

        passed_checks: List[str] = []
        failed_checks: List[str] = []

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
        
        # 4. Calculate final score
        if checks:
            score = len(passed_checks) / len(checks)
        else:
            score = 0.0 # No checks were run

        if verbosity >= 1:
            log_queue.put(f"[{pid}] Quality check for '{dataset_name}' complete. Passed: {len(passed_checks)}/{len(checks)}. Score: {score:.2f}")
        
        if verbosity >= 2 and failed_checks:
            log_queue.put(f"[{pid}] [DEBUG] Failed checks for '{dataset_name}': {', '.join(failed_checks)}")

    except Exception as e:
        if verbosity >0:
            log_queue.put(f"[{pid}] [CRITICAL ERROR] evaluating dataset '{dataset_name}': {e}")
        score = 0.0

    end_time = time.perf_counter()
    time_taken = end_time - start_time
    
    return score, time_taken
