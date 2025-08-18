#!/usr/bin/env python3
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from test_engine import TestEngine

def main():
    engine = TestEngine()
    
    while True:
        try:
            engine.run_all()
            print("cycle completed")
            time.sleep(3600)
        except KeyboardInterrupt:
            print("stopped")
            break
        except Exception as e:
            print(f"error: {e}")
            time.sleep(300)

if __name__ == "__main__":
    main()
