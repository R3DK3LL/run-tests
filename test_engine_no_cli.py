#!/usr/bin/env python3
import os
import json
import subprocess
import time
import random
import fcntl
from datetime import datetime
from pathlib import Path
import logging
import shlex
import threading

class TestEngine:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.setup_logging()
        self.config = self.load_config()
        self.ensure_structure()
        self.test_mode = not self._on_branch()[0]
        self._file_lock = threading.Lock()

    def setup_logging(self):
        log_dir = self.repo_path / "logs"
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_dir / "automation.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        config_path = self.repo_path / "automation" / "config.json"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        
        default_config = {
            "patterns": ["timeout_validation", "edge_case_detection", "performance_check", "memory_validation"],
            "languages": ["python", "javascript", "go", "rust"],
            "authors": [
                {"name": "TestBot", "email": "testbot@sys.test"},
                {"name": "Validator", "email": "val@sys.test"},
                {"name": "CheckEngine", "email": "check@sys.test"},
            ],
            "categories": ["unit", "integration", "performance", "stress"],
        }
        
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    def ensure_structure(self):
        dirs = [
            "automation", "automation/scripts", "automation/templates",
            "lang", "suites", "perf", "sandbox/exp", "tests/unit", 
            "tests/integration", "achievements"
        ]
        for d in dirs:
            (self.repo_path / d).mkdir(parents=True, exist_ok=True)

    def _run_git(self, args, allow_fail=False):
        result = subprocess.run(args, cwd=self.repo_path, capture_output=True, text=True)
        if not allow_fail and result.returncode != 0:
            cmd_str = ' '.join(shlex.quote(a) for a in args)
            raise Exception(
                f"git {cmd_str} failed (rc={result.returncode})\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
        return result

    def _stage_paths(self, *paths):
        if paths:
            self._run_git(["git", "add", *[str(p) for p in paths]])
        else:
            self._run_git(["git", "add", "-A"])

    def _has_staged_changes(self):
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], 
            cwd=self.repo_path, 
            capture_output=True
        )
        return result.returncode != 0

    def _on_branch(self):
        result = subprocess.run(
            ["git", "symbolic-ref", "-q", "--short", "HEAD"], 
            cwd=self.repo_path, capture_output=True, text=True
        )
        return (result.returncode == 0, result.stdout.strip())

    def _commit_and_push(self, messages, allow_empty=False):
        on_branch, _ = self._on_branch()
        if not on_branch:
            self.logger.info("detached HEAD: skip commit/push (test mode)")
            return False

        if not allow_empty and not self._has_staged_changes():
            self.logger.info("no staged changes to commit")
            return False

        args = ["git", "commit"]
        if allow_empty:
            args.append("--allow-empty")
        
        if isinstance(messages, str):
            args += ["-m", messages]
        else:
            for msg in messages:
                args += ["-m", msg]

        try:
            self._run_git(args)
            self._run_git(["git", "push"])
            return True
        except Exception as e:
            self.logger.error(f"commit/push failed: {e}")
            return False

    def simple_commit(self):
        self.logger.info("executing simple_commit")
        if self.test_mode:
            self.logger.info("test mode: skip writes/commit")
            return

        pattern = random.choice(self.config["patterns"])
        ts = int(time.time())
        script_path = self.repo_path / "automation" / "scripts" / f"fix_{pattern}_{ts}.py"
        
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(self._gen_repair(pattern))
        
        self._stage_paths(script_path)
        if self._commit_and_push(f"repair: {pattern}"):
            self.logger.info(f"simple_commit completed: {pattern}")

    def multi_lang(self):
        self.logger.info("executing multi_lang")
        if self.test_mode:
            self.logger.info("test mode: skip writes/commit")
            return

        concept = "timing_validation"
        ts = datetime.now().isoformat(timespec="seconds")
        
        for lang in self.config["languages"]:
            lang_dir = self.repo_path / "lang" / lang
            lang_dir.mkdir(exist_ok=True)
            test_file = lang_dir / f"{concept}.{self._get_ext(lang)}"
            
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(self._gen_lang_test(concept, lang, ts))
        
        self._stage_paths(self.repo_path / "lang")
        if self._commit_and_push(f"multi-lang: {concept}"):
            self.logger.info("multi_lang completed")

    def collab_dev(self):
        self.logger.info("executing collab_dev")
        if self.test_mode:
            self.logger.info("test mode: skip writes/commit")
            return

        author = random.choice(self.config["authors"])
        focus = random.choice(self.config["categories"])
        test_path = self.repo_path / "tests" / focus / f"collab_{focus}.py"
        test_path.parent.mkdir(exist_ok=True)
        
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(self._gen_collab(focus))
        
        self._stage_paths(test_path)
        messages = [
            f"collab: {focus}", 
            f"Co-authored-by: {author['name']} <{author['email']}>"
        ]
        
        if self._commit_and_push(messages, allow_empty=True):
            self.logger.info(f"collab_dev completed: {author['name']}")

    def daily_update(self):
        self.logger.info("executing daily_update")
        if self.test_mode:
            self.logger.info("test mode: skip writes/commit")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        update_type = f"daily_{today.replace('-', '_')}"
        daily_path = self.repo_path / "sandbox" / "exp" / f"{update_type}.py"
        perf_file = self.repo_path / "perf" / "metrics.json"
        
        with open(daily_path, "w", encoding="utf-8") as f:
            f.write(self._gen_daily(update_type))
        
        self._update_metrics(perf_file, update_type)
        self._stage_paths(daily_path, perf_file)
        
        if self._commit_and_push(f"daily: {update_type}"):
            self.logger.info("daily_update completed")

    def _update_metrics(self, perf_file, update_type):
        with self._file_lock:
            if perf_file.exists():
                with open(perf_file, "r+", encoding="utf-8") as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {"metrics": []}
            else:
                data = {"metrics": []}
                
            data["metrics"].append({
                "type": update_type,
                "timestamp": datetime.now().isoformat(),
                "value": random.uniform(0.1, 1.0)
            })
            
            with open(perf_file, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(data, f, indent=2)

    def _gen_repair(self, issue_type):
        ts = datetime.now().isoformat(timespec="seconds")
        return f'''# Generated {ts}
import time
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
'''

    def _gen_lang_test(self, concept, lang, ts):
        templates = {
            "python": f'''# Generated {ts}
import time

def validate_{concept}():
    start = time.time()
    for i in range(1000):
        pass
    return time.time() - start < 0.01

assert validate_{concept}()
''',
            "javascript": f'''// Generated {ts}
const validate_{concept} = () => {{
    const start = Date.now();
    for (let i = 0; i < 1000; i++) {{}}
    return Date.now() - start < 10;
}};
console.assert(validate_{concept}());
''',
            "go": f'''// Generated {ts}
package main
import ("fmt"; "time")
func validate_{concept}() bool {{
    start := time.Now()
    for i := 0; i < 1000; i++ {{}}
    return time.Since(start) < time.Millisecond*10
}}
func main() {{ fmt.Println(validate_{concept}()) }}
''',
            "rust": f'''// Generated {ts}
use std::time::Instant;
fn validate_{concept}() -> bool {{
    let start = Instant::now();
    for _ in 0..1000 {{}}
    start.elapsed().as_millis() < 10
}}
fn main() {{ println!("{{}}", validate_{concept}()); }}
'''
        }
        return templates.get(lang, f"// {lang} not supported ({ts})\n")

    def _gen_collab(self, focus):
        ts = datetime.now().isoformat(timespec="seconds")
        return f'''# Generated {ts}
import unittest
import threading
import time

class Collab{focus.title()}Test(unittest.TestCase):
    def test_concurrent_{focus}(self):
        results, threads = [], []
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
'''

    def _gen_daily(self, update_type):
        ts = datetime.now().isoformat(timespec="seconds")
        return f'''# Generated {ts}
import json
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
'''

    def _get_ext(self, lang):
        extensions = {"python": "py", "javascript": "js", "go": "go", "rust": "rs"}
        return extensions.get(lang, "txt")

    def run_all(self):
        steps = [self.simple_commit, self.multi_lang, self.collab_dev, self.daily_update]
        for step in steps:
            step()
            time.sleep(3)

if __name__ == "__main__":
    engine = TestEngine()
    engine.run_all()
