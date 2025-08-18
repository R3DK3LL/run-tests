import time

def validate_timing_validation():
    start = time.time()
    for i in range(1000):
        pass
    return time.time() - start < 0.01

assert validate_timing_validation()
