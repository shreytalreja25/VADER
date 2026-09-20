import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

class Skill:
    def __init__(self, name: str, description: str, instructions: str, metadata: Dict[str, Any], path: Path):
        self.name = name
        self.description = description
        self.instructions = instructions
        self.metadata = metadata
        self.path = path

class SkillManager:
    """
    Manages extensible developer skills for Vader.
    Skills contain specialized domain instructions, automated actions, and guardrails.
    """
    def __init__(self, workspace_dir: Optional[str] = None):
        self.workspace_dir = Path(workspace_dir or os.getcwd()).resolve()
        self.global_skills_dir = Path.home() / ".vader" / "skills"
        self.local_skills_dir = self.workspace_dir / ".vader" / "skills"
        self.global_skills_dir.mkdir(parents=True, exist_ok=True)
        self.local_skills_dir.mkdir(parents=True, exist_ok=True)

    def list_skills(self) -> List[Skill]:
        skills = []
        # Search local then global
        seen = set()
        for s_dir in [self.local_skills_dir, self.global_skills_dir, self.workspace_dir / "skills"]:
            if s_dir.exists():
                for item in s_dir.iterdir():
                    if item.is_dir() and (item / "SKILL.md").exists():
                        if item.name not in seen:
                            s = self.load_skill(item / "SKILL.md")
                            if s:
                                skills.append(s)
                                seen.add(item.name)
        return skills

    def load_skill(self, skill_file: Path) -> Optional[Skill]:
        try:
            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse YAML frontmatter
            metadata = {}
            body = content
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1]) or {}
                    body = parts[2].strip()

            name = metadata.get("name", skill_file.parent.name)
            desc = metadata.get("description", "No description provided.")
            return Skill(name=name, description=desc, instructions=body, metadata=metadata, path=skill_file.parent)
        except Exception:
            return None

    def install_skill(self, source_path_or_url: str) -> Skill:
        src = Path(source_path_or_url)
        if src.exists() and src.is_dir():
            target = self.global_skills_dir / src.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(src, target)
            skill = self.load_skill(target / "SKILL.md")
            if skill:
                return skill
            raise ValueError("Installed directory does not contain a valid SKILL.md")
        elif source_path_or_url.startswith("http"):
            # Git clone or download
            raise NotImplementedError("Remote URL git installer can be run via: git clone <url> ~/.vader/skills/<name>")
        else:
            raise FileNotFoundError(f"Source skill path not found: {source_path_or_url}")

skill_manager = SkillManager()
