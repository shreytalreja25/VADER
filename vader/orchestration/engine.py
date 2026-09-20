import re
import subprocess
from typing import Dict, Any, List, Optional, Callable
from vader.providers.manager import ProviderManager
from vader.context.harness import ContextHarness
from vader.orchestration.agents import (
    ARCHITECT_SYSTEM_PROMPT,
    CODER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    TESTER_SYSTEM_PROMPT
)
from vader.config import config_manager

class ExecutionStep:
    def __init__(self, step_num: int, description: str, status: str = 'pending'):
        self.step_num = step_num
        self.description = description
        self.status = status

class VaderEngine:
    """
    Autonomous agent orchestration engine implementing the self-healing execution loop.
    """
    def __init__(self, workspace_dir: Optional[str] = None, on_event: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        self.harness = ContextHarness(workspace_dir)
        self.provider = ProviderManager.get_provider()
        self.on_event = on_event or (lambda event, payload: None)
        self.max_repairs = config_manager.get("orchestration.max_repair_iterations", 3)

    def _emit(self, event: str, payload: Dict[str, Any]):
        self.on_event(event, payload)

    def plan_and_execute(self, user_intent: str) -> Dict[str, Any]:
        self._emit("start", {"prompt": user_intent, "model": getattr(self.provider, "model", "unknown")})
        self._emit("phase", {"name": "context_indexing", "msg": "Scanning repository symbol graph..."})
        context_str = self.harness.assemble_context()

        self._emit("phase", {"name": "planning", "msg": "Architect Agent designing execution graph..."})
        architect_prompt = f"Context:\n{context_str}\n\nUser Request: {user_intent}\n\nCreate an architectural execution plan."
        plan_output = self.provider.generate(architect_prompt, system_prompt=ARCHITECT_SYSTEM_PROMPT)
        self._emit("plan_created", {"plan": plan_output})

        target_files = []
        for line in plan_output.splitlines():
            m = re.search(r"(\b[\w\-./\\]+\.[a-zA-Z0-9]+\b)", line)
            if m and not line.startswith("CRITICAL") and not line.startswith("VERIFICATION"):
                f = m.group(1).replace("\\", "/")
                if f not in target_files and "." in f:
                    target_files.append(f)

        self._emit("phase", {"name": "coding", "msg": "Coder Agent generating multi-file changes..."})
        coder_prompt = f"Architect Plan:\n{plan_output}\n\nUser Intent: {user_intent}\n\nContext:\n{self.harness.assemble_context(relevant_files=target_files[:3])}\n\nImplement all requested changes with complete files."
        code_output = self.provider.generate(coder_prompt, system_prompt=CODER_SYSTEM_PROMPT)
        applied_files = self._apply_code_blocks(code_output)
        self._emit("files_written", {"files": applied_files})

        self._emit("phase", {"name": "verification", "msg": "Testing & self-healing sandbox validation..."})
        verification_passed, error_log = self._run_sandbox_checks()

        repair_count = 0
        while not verification_passed and repair_count < self.max_repairs:
            repair_count += 1
            self._emit("self_healing", {"iteration": repair_count, "error": error_log[:500]})
            tester_prompt = f"Test / Lint failure encountered:\nError:\n{error_log}\n\nActive Git Diff:\n{self.harness.get_git_diff()[:2000]}\n\nDiagnose and provide the corrected code for the failing file."
            repair_output = self.provider.generate(tester_prompt, system_prompt=TESTER_SYSTEM_PROMPT)
            self._apply_code_blocks(repair_output)
            verification_passed, error_log = self._run_sandbox_checks()

        self._emit("phase", {"name": "review", "msg": "Reviewer Agent validating security & guardrails..."})
        review_prompt = f"Review the final diffs:\n{self.harness.get_git_diff()[:3000]}\n\nOriginal Request: {user_intent}"
        review_output = self.provider.generate(review_prompt, system_prompt=REVIEWER_SYSTEM_PROMPT)

        result = {
            'success': verification_passed or repair_count < self.max_repairs,
            'repairs_attempted': repair_count,
            'modified_files': applied_files,
            'plan': plan_output,
            'review': review_output
        }
        self._emit("complete", result)
        return result

    def _apply_code_blocks(self, text: str) -> List[str]:
        applied = []
        pattern = r'FILE:[ \t]*([^\r\n]+)[\r\n]+```[a-zA-Z0-9_\-]*[\r\n]+(.*?)```'
        file_matches = re.finditer(pattern, text, re.DOTALL)
        for match in file_matches:
            file_path = match.group(1).strip()
            content = match.group(2)
            try:
                self.harness.write_file(file_path, content)
                applied.append(file_path)
            except Exception as e:
                self._emit("error", {"msg": f"Failed to write {file_path}: {e}"})
        return applied

    def _run_sandbox_checks(self) -> tuple:
        root = self.harness.root_dir
        check_cmd = None
        if (root / "pytest.ini").exists() or (root / "pyproject.toml").exists() or list(root.glob("test_*.py")):
            check_cmd = ["pytest", "-q"]
        elif (root / "package.json").exists():
            check_cmd = ["npm", "test"]

        if not check_cmd:
            return True, "No automated test suite detected."

        try:
            res = subprocess.run(
                check_cmd,
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=config_manager.get("orchestration.sandbox_timeout", 60)
            )
            if res.returncode == 0:
                return True, res.stdout
            else:
                return False, f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        except FileNotFoundError:
            return True, "Test runner binary not found, skipping."
        except subprocess.TimeoutExpired:
            return False, "Execution timeout in sandbox."
        except Exception as e:
            return False, str(e)
