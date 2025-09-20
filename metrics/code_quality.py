import subprocess

def get_pylint_score(file_path: str) -> float:
    """
    Compute PyLint score for a Python file robustly.

    Args:
        file_path (str): Path to the Python file.

    Returns:
        float: PyLint score (0–10)
    """
    try:
        # Run PyLint and capture output
        result = subprocess.run(
            ["pylint", file_path, "--score=y"],
            capture_output=True,
            text=True
        )

        # Look for line that contains the score
        for line in result.stdout.splitlines():
            if "Your code has been rated at" in line:
                # Example: 'Your code has been rated at 8.56/10'
                parts = line.split(" ")
                for part in parts:
                    if "/" in part:
                        score_str = part.split("/")[0]
                        return float(score_str) / 10
        
        # Fallback if not found
        return 0.0

    except Exception as e:
        print("Error running PyLint:", e)
        return 0.0

if __name__ == "__main__":
    score = get_pylint_score("./classes/api.py")
    print("PyLint code quality score:", score)
