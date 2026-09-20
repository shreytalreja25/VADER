import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from vader.config import config_manager

class ContextHarness:
    """
    Multi-File Repository Context Harness.
    Builds symbol trees, extracts AST definitions, monitors git diffs,
    and constructs token-budgeted prompt context.
    """
    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir or os.getcwd()).resolve()
        self.protected_paths = config_manager.get("guardrails.protected_paths", [".git", ".env", "node_modules", "venv"])

    def is_ignored(self, path: Path) -> bool:
        parts = path.relative_to(self.root_dir).parts
        for part in parts:
            if part in self.protected_paths or part.startswith(".") and part != ".":
                return True
        return False

    def scan_repository(self, max_files: int = 150) -> List[Dict[str, Any]]:
        file_list = []
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if not self.is_ignored(Path(root) / d)]
            for file in files:
                fpath = Path(root) / file
                if not self.is_ignored(fpath):
                    try:
                        rel_path = str(fpath.relative_to(self.root_dir))
                        size = fpath.stat().st_size
                        if size < 500_000:  # Skip large binary files
                            file_list.append({
                                "path": rel_path,
                                "size": size,
                                "extension": fpath.suffix
                            })
                    except Exception:
                        continue
                if len(file_list) >= max_files:
                    break
            if len(file_list) >= max_files:
                break
        return file_list

    def extract_symbols(self, file_path: str) -> List[Dict[str, Any]]:
        full_path = self.root_dir / file_path
        if not full_path.exists():
            return []
        
        symbols = []
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            
            suffix = full_path.suffix.lower()
            for idx, line in enumerate(lines):
                # Python symbols
                if suffix == ".py":
                    m_def = re.match(r"^\s*(def|class)\s+([a-zA-Z_0-9]+)", line)
                    if m_def:
                        symbols.append({
                            "type": m_def.group(1),
                            "name": m_def.group(2),
                            "line": idx + 1
                        })
                # JS / TS symbols
                elif suffix in [".js", ".ts", ".jsx", ".tsx"]:
                    m_fn = re.match(r"^\s*(export\s+)?(function|class|interface|type|const)\s+([a-zA-Z_0-9]+)", line)
                    if m_fn:
                        symbols.append({
                            "type": m_fn.group(2),
                            "name": m_fn.group(3),
                            "line": idx + 1
                        })
        except Exception:
            pass
        return symbols

    def get_git_diff(self) -> str:
        try:
            res = subprocess.run(
                ["git", "diff", "HEAD"],
                cwd=str(self.root_dir),
                capture_output=True,
                text=True,
                timeout=5
            )
            return res.stdout.strip()
        except Exception:
            return ""

    def get_git_status(self) -> str:
        try:
            res = subprocess.run(
                ["git", "status", "--short"],
                cwd=str(self.root_dir),
                capture_output=True,
                text=True,
                timeout=5
            )
            return res.stdout.strip()
        except Exception:
            return ""

    def read_file(self, rel_path: str) -> Optional[str]:
        p = self.root_dir / rel_path
        if p.exists() and p.is_file():
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    return f.read()
            except Exception:
                return None
        return None

    def write_file(self, rel_path: str, content: str):
        p = self.root_dir / rel_path
        # Guardrail check
        for prot in self.protected_paths:
            if prot in p.parts:
                raise PermissionError(f"Cannot mutate protected path: {rel_path}")
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)

    def assemble_context(self, relevant_files: Optional[List[str]] = None) -> str:
        manifest = self.scan_repository(max_files=40)
        tree_summary = "\n".join([f"- {item['path']} ({item['size']} bytes)" for item in manifest])
        
        content_snippets = []
        if relevant_files:
            for rf in relevant_files[:5]:
                body = self.read_file(rf)
                if body is not None:
                    # Truncate to avoid context window explosion on 4k/8k local models
                    snippet = body[:3000]
                    content_snippets.append(f"### File: {rf}\n```\n{snippet}\n```")
        
        status = self.get_git_status()
        git_sec = f"\n### Git Status:\n{status}" if status else ""

        return f"""Repository File Tree:
{tree_summary}
{git_sec}

{"\n\n".join(content_snippets)}
"""
