import time
import subprocess
from pathlib import Path


def validate_performance_check():
    start = time.time()
    result = subprocess.run(["python", "-c", 'print("test")'], capture_output=True)
    duration = time.time() - start
    return duration < 0.1 and result.returncode == 0


def repair_performance_check():
    if not validate_performance_check():
        Path("temp_fix.txt").write_text(f"repaired at {time.time()}")
        return True
    return False


if __name__ == "__main__":
    repair_performance_check()
