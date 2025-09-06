#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from test_engine import TestEngine


def main():
    engine = TestEngine()

    if len(sys.argv) > 1:
        method = sys.argv[1]
        if hasattr(engine, method):
            getattr(engine, method)()
        else:
            print(f"method {method} not found")
    else:
        engine.run_all()


if __name__ == "__main__":
    main()
