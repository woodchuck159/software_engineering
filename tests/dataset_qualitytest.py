from datasets import load_dataset
import pandas as pd

def test_dataset(dataset_name: str, split: str = "train") -> None:
    # Load dataset from Hugging Face
    ds = load_dataset(dataset_name, split=split)
    df = ds.to_pandas()

    print(f"✅ Loaded dataset '{dataset_name}' split '{split}'")
    print(f"Rows: {len(df)}, Columns: {list(df.columns)}")

    # Basic quality checks
    print("\n🔍 Running quality checks...")
    missing = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()

    print(f"- Missing values: {missing}")
    print(f"- Duplicate rows: {duplicates}")
    print(f"- Row count > 0: {len(df) > 0}")

    # Simple score
    checks = 3
    passed = sum([
        missing == 0,
        duplicates == 0,
        len(df) > 0
    ])
    score = round(passed / checks * 100, 2)
    print(f"\n⭐ Dataset quality score: {score}%")

if __name__ == "__main__":
    test_dataset("imdb", "train")   # example dataset
