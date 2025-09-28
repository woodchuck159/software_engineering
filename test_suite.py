import sys
import subprocess
from pathlib import Path


def run_coverage(source_dir: str, tests_dir: str) -> None:
    """
    Run pytest with coverage measurement.

    Args:
        source_dir (str): Directory containing your source code.
        tests_dir (str): Directory containing your tests.
    """
    src = Path(source_dir)
    tst = Path(tests_dir)

    if not src.exists() or not tst.exists():
        print(f"Error: source '{source_dir}' or tests '{tests_dir}' not found.")
        sys.exit(1)

    # Run coverage with pytest
    cmd = ["coverage", "run", f"--source={src}", "-m", "pytest", str(tst), "-q"]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=False)

    # Show reports
    subprocess.run(["coverage", "report", "-m"], check=False)
    subprocess.run(["coverage", "html"], check=False)


if __name__ == "__main__":
    # Example usage (update to match your project layout)
    run_coverage("my_project", "tests")
