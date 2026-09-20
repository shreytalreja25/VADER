import os
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from vader.orchestration.engine import VaderEngine

class WorkflowStep:
    def __init__(self, id: str, name: str, type: str, config: Dict[str, Any]):
        self.id = id
        self.name = name
        self.type = type # 'agent', 'command', 'skill', 'assert'
        self.config = config

class Workflow:
    def __init__(self, name: str, description: str, steps: List[WorkflowStep]):
        self.name = name
        self.description = description
        self.steps = steps

class WorkflowEngine:
    """
    Executes multi-step agentic pipelines defined in YAML.
    """
    def __init__(self, workspace_dir: Optional[str] = None):
        self.workspace_dir = Path(workspace_dir or os.getcwd()).resolve()

    def load_workflow(self, file_path: str) -> Workflow:
        p = Path(file_path)
        if not p.is_absolute():
            # Check local .vader/workflows or workflows/
            candidates = [
                self.workspace_dir / file_path,
                self.workspace_dir / ".vader" / "workflows" / file_path,
                self.workspace_dir / "workflows" / file_path,
            ]
            for c in candidates:
                if c.exists():
                    p = c
                    break
        
        if not p.exists():
            raise FileNotFoundError(f"Workflow file not found: {file_path}")

        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        steps = []
        for s in data.get("steps", []):
            steps.append(WorkflowStep(
                id=s.get("id", "step"),
                name=s.get("name", "Unnamed Step"),
                type=s.get("type", "command"),
                config=s
            ))

        return Workflow(
            name=data.get("name", p.stem),
            description=data.get("description", ""),
            steps=steps
        )

    def execute(self, workflow: Workflow, on_step_update=None) -> bool:
        engine = VaderEngine(str(self.workspace_dir))
        for step in workflow.steps:
            if on_step_update:
                on_step_update(step, "running")

            if step.type == "agent":
                prompt = step.config.get("prompt", "")
                res = engine.plan_and_execute(prompt)
                if not res.get("success", False):
                    if on_step_update:
                        on_step_update(step, "failed")
                    return False
            elif step.type == "command":
                cmd = step.config.get("run", "")
                res = subprocess.run(cmd, shell=True, cwd=str(self.workspace_dir), capture_output=True, text=True)
                if res.returncode != 0:
                    if on_step_update:
                        on_step_update(step, "failed")
                    return False
            
            if on_step_update:
                on_step_update(step, "completed")

        return True
