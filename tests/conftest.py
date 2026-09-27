"""
Pytest configuration and shared fixtures for VADER tests.
"""
import os
import sys
import pytest
from pathlib import Path


# Add vader package to Python path
vader_root = Path(__file__).parent.parent
sys.path.insert(0, str(vader_root))


@pytest.fixture
def clean_env(monkeypatch):
    """Provide clean environment without user configs."""
    # Clear environment variables that might affect tests
    env_vars = [
        "VADER_PROVIDER",
        "VADER_MODEL",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
    ]

    for var in env_vars:
        monkeypatch.delenv(var, raising=False)

    yield


@pytest.fixture
def isolated_workspace(tmp_path):
    """Provide isolated workspace directory for tests."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Save original directory
    original_dir = os.getcwd()

    # Change to workspace
    os.chdir(workspace)

    yield workspace

    # Restore original directory
    os.chdir(original_dir)


@pytest.fixture
def sample_skill(tmp_path):
    """Create a sample skill for testing."""
    skill_dir = tmp_path / "sample-skill"
    skill_dir.mkdir()

    skill_content = """---
name: sample-skill
description: A sample skill for testing
author: Test Suite
version: 1.0.0
tags:
  - testing
  - sample
---

# Sample Skill

This skill provides sample instructions for testing purposes.

## Usage

Use this skill when testing the skills management system.

## Instructions

1. Always validate input
2. Generate clean code
3. Follow best practices
"""

    (skill_dir / "SKILL.md").write_text(skill_content)

    return skill_dir


@pytest.fixture
def sample_workflow(tmp_path):
    """Create a sample workflow for testing."""
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir()

    workflow_content = """
name: sample-workflow
description: A sample workflow for testing

steps:
  - id: step_1
    name: First Step
    type: command
    run: echo "Step 1 executed"

  - id: step_2
    name: Second Step
    type: command
    run: echo "Step 2 executed"

  - id: step_3
    name: Third Step
    type: command
    run: echo "Step 3 executed"
"""

    workflow_file = workflows_dir / "sample.yaml"
    workflow_file.write_text(workflow_content)

    return workflow_file


@pytest.fixture
def mock_git_repo(tmp_path):
    """Create a mock git repository for testing."""
    import subprocess

    repo_dir = tmp_path / "git_repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(
        ["git", "init"],
        cwd=str(repo_dir),
        capture_output=True,
        check=False
    )

    # Configure git user
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo_dir),
        capture_output=True,
        check=False
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo_dir),
        capture_output=True,
        check=False
    )

    # Create initial commit
    (repo_dir / "README.md").write_text("# Test Repo")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=str(repo_dir),
        capture_output=True,
        check=False
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=str(repo_dir),
        capture_output=True,
        check=False
    )

    return repo_dir


@pytest.fixture
def sample_python_project(tmp_path):
    """Create a sample Python project structure."""
    project_dir = tmp_path / "python_project"
    project_dir.mkdir()

    # Create source directory
    src_dir = project_dir / "src"
    src_dir.mkdir()

    # Create main module
    (src_dir / "__init__.py").write_text("")
    (src_dir / "main.py").write_text("""
def main():
    \"\"\"Main entry point.\"\"\"
    print("Hello from VADER")

if __name__ == "__main__":
    main()
""")

    # Create utility module
    (src_dir / "utils.py").write_text("""
def helper_function(x):
    \"\"\"A helper function.\"\"\"
    return x * 2

class UtilityClass:
    \"\"\"A utility class.\"\"\"

    def __init__(self, value):
        self.value = value

    def process(self):
        return self.value + 1
""")

    # Create tests directory
    tests_dir = project_dir / "tests"
    tests_dir.mkdir()

    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_main.py").write_text("""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import helper_function

def test_helper_function():
    assert helper_function(5) == 10
""")

    # Create setup files
    (project_dir / "pyproject.toml").write_text("""
[project]
name = "sample-project"
version = "0.1.0"

[tool.pytest.ini_options]
testpaths = ["tests"]
""")

    return project_dir


# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers",
        "cli: marks tests that require CLI installation"
    )
