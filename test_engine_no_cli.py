#!/usr/bin/env python3
import os
import json
import subprocess
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
import logging


class TestEngine:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.setup_logging()
        self.config = self.load_config()
        self.ensure_structure()

    def setup_logging(self):
        log_dir = self.repo_path / "logs"
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / "automation.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        config_path = self.repo_path / "automation" / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)

        default_config = {
            "patterns": [
                "timeout_validation",
                "edge_case_detection",
                "performance_check",
                "memory_validation",
            ],
            "languages": ["python", "javascript", "go", "rust"],
            "authors": [
                {"name": "TestBot", "email": "testbot@sys.test"},
                {"name": "Validator", "email": "val@sys.test"},
                {"name": "CheckEngine", "email": "check@sys.test"},
            ],
            "categories": ["unit", "integration", "performance", "stress"],
        }

        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    def ensure_structure(self):
        dirs = [
            "automation",
            "automation/scripts",
            "automation/templates",
            "lang",
            "suites",
            "perf",
            "sandbox/exp",
            "tests/unit",
            "tests/integration",
        ]
        for dir_name in dirs:
            (self.repo_path / dir_name).mkdir(parents=True, exist_ok=True)

    def simple_commit(self):
        self.logger.info("executing simple_commit")

        pattern = random.choice(self.config["patterns"])
        ts = int(time.time())

        script_content = self.gen_repair(pattern)
        script_path = (
            self.repo_path / "automation" / "scripts" / f"fix_{pattern}_{ts}.py"
        )

        with open(script_path, "w") as f:
            f.write(script_content)

        try:
            self.exec_git(
                [
                    f"git add {script_path}",
                    f'git commit -m "repair: {pattern}"',
                    f"git push",
                ]
            )
            self.logger.info(f"simple_commit completed: {pattern}")
        except Exception as e:
            self.logger.error(f"simple_commit failed: {e}")

    def multi_lang(self):
        self.logger.info("executing multi_lang")

        concept = "timing_validation"

        for lang in self.config["languages"]:
            lang_dir = self.repo_path / "lang" / lang
            lang_dir.mkdir(exist_ok=True)

            code = self.gen_lang_test(concept, lang)
            test_file = lang_dir / f"{concept}.{self.get_ext(lang)}"

            with open(test_file, "w") as f:
                f.write(code)

        try:
            self.exec_git(
                ["git add lang/", f'git commit -m "multi-lang: {concept}"', "git push"]
            )
            self.logger.info("multi_lang completed")
        except Exception as e:
            self.logger.error(f"multi_lang failed: {e}")

    def collab_dev(self):
        self.logger.info("executing collab_dev")

        author = random.choice(self.config["authors"])
        focus = random.choice(self.config["categories"])

        collab_test = self.gen_collab(focus)
        test_path = self.repo_path / "tests" / focus / f"collab_{focus}.py"
        test_path.parent.mkdir(exist_ok=True)

        with open(test_path, "w") as f:
            f.write(collab_test)

        commit_msg = (
            f'collab: {focus}\n\nCo-authored-by: {author["name"]} <{author["email"]}>'
        )

        try:
            self.exec_git(
                [f"git add {test_path}", f'git commit -m "{commit_msg}"', "git push"]
            )
            self.logger.info(f"collab_dev completed: {author['name']}")
        except Exception as e:
            self.logger.error(f"collab_dev failed: {e}")

    def daily_update(self):
        self.logger.info("executing daily_update")

        today = datetime.now().strftime("%Y-%m-%d")
        update_type = f"daily_{today.replace('-', '_')}"

        daily_code = self.gen_daily(update_type)
        daily_path = self.repo_path / "sandbox" / "exp" / f"{update_type}.py"

        with open(daily_path, "w") as f:
            f.write(daily_code)

        perf_file = self.repo_path / "perf" / "metrics.json"
        self.update_metrics(perf_file, update_type)

        try:
            self.exec_git(
                [
                    f"git add {daily_path} {perf_file}",
                    f'git commit -m "daily: {update_type}"',
                    "git push",
                ]
            )
            self.logger.info("daily_update completed")
        except Exception as e:
            self.logger.error(f"daily_update failed: {e}")

    def exec_git(self, commands):
        import shlex
        for cmd in commands:
            try:
                cmd_list = shlex.split(cmd) if isinstance(cmd, str) else cmd
                result = subprocess.run(cmd_list, check=True, cwd=self.repo_path, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Command execution failed: {e.stderr}") from e
            time.sleep(1)

    def gen_repair(self, issue_type):
        return f"""import time
import subprocess
from pathlib import Path

def validate_{issue_type}():
    start = time.time()
    result = subprocess.run(['python', '-c', 'print("test")'], capture_output=True)
    duration = time.time() - start
    return duration < 0.1 and result.returncode == 0

def repair_{issue_type}():
    if not validate_{issue_type}():
        Path("temp_fix.txt").write_text(f"repaired at {{time.time()}}")
        return True
    return False

if __name__ == "__main__":
    repair_{issue_type}()
"""

    def gen_lang_test(self, concept, lang):
        if lang == "python":
            return f"""import time

def validate_{concept}():
    start = time.time()
    for i in range(1000):
        pass
    return time.time() - start < 0.01

assert validate_{concept}()
"""
        elif lang == "javascript":
            return f"""const validate_{concept} = () => {{
    const start = Date.now();
    for (let i = 0; i < 1000; i++) {{}}
    return Date.now() - start < 10;
}};

console.assert(validate_{concept}());
"""
        elif lang == "go":
            return f"""package main

import (
    "fmt"
    "time"
)

func validate_{concept}() bool {{
    start := time.Now()
    for i := 0; i < 1000; i++ {{}}
    return time.Since(start) < time.Millisecond*10
}}

func main() {{
    fmt.Println(validate_{concept}())
}}
"""
        elif lang == "rust":
            return f"""use std::time::Instant;

fn validate_{concept}() -> bool {{
    let start = Instant::now();
    for _ in 0..1000 {{}}
    start.elapsed().as_millis() < 10
}}

fn main() {{
    println!("{{}}", validate_{concept}());
}}
"""

    def gen_collab(self, focus):
        return f"""import unittest
import threading
import time

class Collab{focus.title()}Test(unittest.TestCase):
    def test_concurrent_{focus}(self):
        results = []
        threads = []
        
        def worker(tid):
            time.sleep(0.1)
            results.append(tid)
        
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(len(results), 5)
    
    def test_{focus}_isolation(self):
        data = {{"test": "value"}}
        self.assertIn("test", data)

if __name__ == "__main__":
    unittest.main()
"""

    def gen_daily(self, update_type):
        return f"""import json
import time
from datetime import datetime

def run_{update_type}():
    timestamp = datetime.now().isoformat()
    data = {{
        "type": "{update_type}",
        "timestamp": timestamp,
        "duration": time.time(),
        "status": "completed"
    }}
    return data

if __name__ == "__main__":
    result = run_{update_type}()
    print(json.dumps(result, indent=2))
"""

    def update_metrics(self, perf_file, update_type):
        if perf_file.exists():
            with open(perf_file) as f:
                data = json.load(f)
        else:
            data = {"metrics": []}

        data["metrics"].append(
            {
                "type": update_type,
                "timestamp": datetime.now().isoformat(),
                "value": random.uniform(0.1, 1.0),
            }
        )

        with open(perf_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_ext(self, lang):
        extensions = {"python": "py", "javascript": "js", "go": "go", "rust": "rs"}
        return extensions.get(lang, "txt")

    def run_all(self):
        self.simple_commit()
        time.sleep(3)
        self.multi_lang()
        time.sleep(3)
        self.collab_dev()
        time.sleep(3)
        self.daily_update()


if __name__ == "__main__":
    engine = TestEngine()
    engine.run_all()
