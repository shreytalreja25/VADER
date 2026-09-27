"""
Functional tests for VADER skills management system.
Tests skill loading, listing, installation, and metadata parsing.
"""
import pytest
from pathlib import Path
from vader.skills.manager import SkillManager, Skill


class TestSkillManager:
    """Test skills manager initialization and directory setup."""

    def test_skill_manager_initialization(self, tmp_path):
        """Test that skill manager initializes with proper directories."""
        skill_mgr = SkillManager(workspace_dir=str(tmp_path))

        assert skill_mgr.workspace_dir == tmp_path
        assert skill_mgr.global_skills_dir.exists()
        assert skill_mgr.local_skills_dir.exists()

    def test_skill_directories_created(self, tmp_path):
        """Test that skill directories are created automatically."""
        skill_mgr = SkillManager(workspace_dir=str(tmp_path))

        local_dir = tmp_path / ".vader" / "skills"
        assert local_dir.exists()
        assert local_dir.is_dir()


class TestSkillLoading:
    """Test skill loading from SKILL.md files."""

    def test_load_skill_with_frontmatter(self, tmp_path):
        """Test loading skill with YAML frontmatter."""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        skill_content = """---
name: test-skill
description: A test skill for validation
version: 1.0.0
---

# Test Skill Instructions

This is a test skill for functional testing.
"""
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_content)

        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skill = skill_mgr.load_skill(skill_file)

        assert skill is not None
        assert skill.name == "test-skill"
        assert skill.description == "A test skill for validation"
        assert "Test Skill Instructions" in skill.instructions

    def test_load_skill_without_frontmatter(self, tmp_path):
        """Test loading skill without YAML frontmatter."""
        skill_dir = tmp_path / "simple-skill"
        skill_dir.mkdir()

        skill_content = """# Simple Skill

Just plain content without frontmatter.
"""
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_content)

        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skill = skill_mgr.load_skill(skill_file)

        assert skill is not None
        assert skill.name == "simple-skill"  # Should use directory name
        assert "No description provided" in skill.description

    def test_load_skill_with_metadata(self, tmp_path):
        """Test loading skill with additional metadata fields."""
        skill_dir = tmp_path / "meta-skill"
        skill_dir.mkdir()

        skill_content = """---
name: meta-skill
description: Skill with metadata
author: Test Author
tags:
  - testing
  - validation
---

Skill with custom metadata.
"""
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_content)

        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skill = skill_mgr.load_skill(skill_file)

        assert skill is not None
        assert skill.metadata["author"] == "Test Author"
        assert "testing" in skill.metadata["tags"]
        assert "validation" in skill.metadata["tags"]

    def test_load_nonexistent_skill(self, tmp_path):
        """Test loading skill that doesn't exist returns None."""
        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skill_file = tmp_path / "nonexistent" / "SKILL.md"

        skill = skill_mgr.load_skill(skill_file)
        assert skill is None

    def test_load_malformed_skill(self, tmp_path):
        """Test loading skill with malformed YAML returns None."""
        skill_dir = tmp_path / "malformed-skill"
        skill_dir.mkdir()

        skill_content = """---
name: malformed
description: [unclosed array
---

Content after malformed YAML.
"""
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_content)

        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skill = skill_mgr.load_skill(skill_file)

        # Should handle malformed YAML gracefully
        assert skill is None or skill.name == "malformed-skill"


class TestSkillListing:
    """Test listing available skills."""

    def test_list_skills_empty(self, tmp_path):
        """Test listing skills when none are installed."""
        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skills = skill_mgr.list_skills()

        # May return empty list or built-in skills
        assert isinstance(skills, list)

    def test_list_skills_with_local_skills(self, tmp_path):
        """Test listing skills from local directory."""
        # Create local skill
        local_skills_dir = tmp_path / ".vader" / "skills"
        local_skills_dir.mkdir(parents=True, exist_ok=True)

        skill_dir = local_skills_dir / "local-skill"
        skill_dir.mkdir()

        skill_content = """---
name: local-skill
description: Local test skill
---

Local skill content.
"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skills = skill_mgr.list_skills()

        skill_names = [s.name for s in skills]
        assert "local-skill" in skill_names

    def test_list_skills_from_workspace(self, tmp_path):
        """Test listing skills from workspace skills directory."""
        # Create workspace skill
        workspace_skills_dir = tmp_path / "skills"
        workspace_skills_dir.mkdir(parents=True, exist_ok=True)

        skill_dir = workspace_skills_dir / "workspace-skill"
        skill_dir.mkdir()

        skill_content = """---
name: workspace-skill
description: Workspace test skill
---

Workspace skill content.
"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skills = skill_mgr.list_skills()

        skill_names = [s.name for s in skills]
        assert "workspace-skill" in skill_names

    def test_list_skills_deduplication(self, tmp_path):
        """Test that duplicate skill names are deduplicated."""
        # Create same skill in multiple locations
        for subdir in [".vader/skills", "skills"]:
            skill_dir = tmp_path / subdir / "duplicate-skill"
            skill_dir.mkdir(parents=True, exist_ok=True)

            skill_content = """---
name: duplicate-skill
description: Duplicate test skill
---

Content.
"""
            (skill_dir / "SKILL.md").write_text(skill_content)

        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skills = skill_mgr.list_skills()

        # Should only have one instance
        duplicate_skills = [s for s in skills if s.name == "duplicate-skill"]
        assert len(duplicate_skills) == 1

    def test_list_skills_multiple(self, tmp_path):
        """Test listing multiple skills."""
        workspace_skills_dir = tmp_path / "skills"
        workspace_skills_dir.mkdir(parents=True, exist_ok=True)

        for i in range(3):
            skill_dir = workspace_skills_dir / f"skill-{i}"
            skill_dir.mkdir()

            skill_content = f"""---
name: skill-{i}
description: Test skill {i}
---

Skill {i} content.
"""
            (skill_dir / "SKILL.md").write_text(skill_content)

        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skills = skill_mgr.list_skills()

        skill_names = [s.name for s in skills]
        assert "skill-0" in skill_names
        assert "skill-1" in skill_names
        assert "skill-2" in skill_names


class TestSkillInstallation:
    """Test skill installation from local directories."""

    def test_install_skill_from_local_directory(self, tmp_path):
        """Test installing skill from local directory."""
        # Create source skill directory
        source_dir = tmp_path / "source-skill"
        source_dir.mkdir()

        skill_content = """---
name: installed-skill
description: Skill to install
---

Installation test content.
"""
        (source_dir / "SKILL.md").write_text(skill_content)

        # Create workspace for installation
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        skill_mgr = SkillManager(workspace_dir=str(workspace_dir))
        skill = skill_mgr.install_skill(str(source_dir))

        assert skill is not None
        assert skill.name == "installed-skill"

        # Verify skill was copied to global directory
        installed_path = skill_mgr.global_skills_dir / source_dir.name
        assert installed_path.exists()
        assert (installed_path / "SKILL.md").exists()

    def test_install_skill_with_additional_files(self, tmp_path):
        """Test installing skill with additional resource files."""
        # Create source skill with multiple files
        source_dir = tmp_path / "multi-file-skill"
        source_dir.mkdir()

        (source_dir / "SKILL.md").write_text("---\nname: multi-file\n---\nContent.")
        (source_dir / "template.txt").write_text("Template content")
        (source_dir / "config.json").write_text('{"key": "value"}')

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        skill_mgr = SkillManager(workspace_dir=str(workspace_dir))
        skill = skill_mgr.install_skill(str(source_dir))

        assert skill is not None

        # Verify all files were copied
        installed_path = skill_mgr.global_skills_dir / source_dir.name
        assert (installed_path / "SKILL.md").exists()
        assert (installed_path / "template.txt").exists()
        assert (installed_path / "config.json").exists()

    def test_install_skill_overwrites_existing(self, tmp_path):
        """Test that installing skill overwrites existing installation."""
        source_dir = tmp_path / "update-skill"
        source_dir.mkdir()

        # Install first version
        (source_dir / "SKILL.md").write_text("---\nname: update\n---\nVersion 1")

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        skill_mgr = SkillManager(workspace_dir=str(workspace_dir))
        skill_v1 = skill_mgr.install_skill(str(source_dir))

        # Update and reinstall
        (source_dir / "SKILL.md").write_text("---\nname: update\n---\nVersion 2")
        skill_v2 = skill_mgr.install_skill(str(source_dir))

        assert skill_v2 is not None
        assert "Version 2" in skill_v2.instructions
        assert "Version 1" not in skill_v2.instructions

    def test_install_skill_nonexistent_directory(self, tmp_path):
        """Test installing skill from nonexistent directory raises error."""
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        skill_mgr = SkillManager(workspace_dir=str(workspace_dir))

        with pytest.raises(FileNotFoundError):
            skill_mgr.install_skill(str(tmp_path / "nonexistent"))

    def test_install_skill_missing_skill_file(self, tmp_path):
        """Test installing directory without SKILL.md raises error."""
        source_dir = tmp_path / "invalid-skill"
        source_dir.mkdir()
        # Don't create SKILL.md

        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        skill_mgr = SkillManager(workspace_dir=str(workspace_dir))

        with pytest.raises(ValueError):
            skill_mgr.install_skill(str(source_dir))


class TestSkillObject:
    """Test Skill object properties."""

    def test_skill_attributes(self, tmp_path):
        """Test that Skill object has expected attributes."""
        skill_dir = tmp_path / "attr-skill"
        skill_dir.mkdir()

        skill_content = """---
name: attr-skill
description: Attribute test
custom: value
---

Instructions here.
"""
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_content)

        skill_mgr = SkillManager(workspace_dir=str(tmp_path))
        skill = skill_mgr.load_skill(skill_file)

        assert hasattr(skill, 'name')
        assert hasattr(skill, 'description')
        assert hasattr(skill, 'instructions')
        assert hasattr(skill, 'metadata')
        assert hasattr(skill, 'path')

        assert skill.name == "attr-skill"
        assert skill.description == "Attribute test"
        assert "Instructions here" in skill.instructions
        assert skill.metadata["custom"] == "value"
        assert skill.path == skill_dir
