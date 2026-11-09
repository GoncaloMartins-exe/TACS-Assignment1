import subprocess
import sys

INSTANCES = [
    "input/4x4_two_queens.json",
    "input/4x4_one_queen.json",
    "input/5x5_two_queens.json",
]

for file in INSTANCES:
    print("\n========================================")
    print(f"Executing pipeline for {file}")
    print("========================================")

    result = subprocess.run(
        [sys.executable, "pipeline.py", file]
    )

    if result.returncode != 0:
        sys.exit(result.returncode)