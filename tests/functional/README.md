# VADER Functional Tests

Comprehensive functional test suite for the VADER autonomous agentic development platform.

## Overview

These tests verify end-to-end behavior of VADER components including:

- **Providers** - LLM provider integrations (Mock, Ollama, Cloud)
- **Configuration** - Config management and persistence
- **Skills** - Skill loading, installation, and management
- **Workflows** - Multi-step workflow execution
- **Context Harness** - Repository scanning and git operations
- **Orchestration** - Multi-agent orchestration engine
- **CLI** - Command-line interface functionality

## Requirements

```bash
# Install test dependencies
pip install pytest pytest-timeout

# Install VADER in development mode
pip install -e .
```

## Running Tests

### Run all functional tests
```bash
pytest tests/functional/
```

### Run specific test file
```bash
pytest tests/functional/test_providers.py
```

### Run specific test class
```bash
pytest tests/functional/test_providers.py::TestMockProvider
```

### Run specific test function
```bash
pytest tests/functional/test_providers.py::TestMockProvider::test_mock_provider_health_check
```

### Run with verbose output
```bash
pytest tests/functional/ -v
```

### Run tests in parallel (requires pytest-xdist)
```bash
pytest tests/functional/ -n auto
```

### Run tests with coverage (requires pytest-cov)
```bash
pytest tests/functional/ --cov=vader --cov-report=html
```

### Skip slow tests
```bash
pytest tests/functional/ -m "not slow"
```

### Skip CLI tests (if CLI not installed)
```bash
pytest tests/functional/ -m "not cli"
```

## Test Categories

### Provider Tests (`test_providers.py`)
Tests LLM provider functionality:
- Health checks
- Model listing
- Response generation
- Streaming
- Provider manager

**Key scenarios:**
- Mock provider for testing
- Provider interface compliance
- Generation with various inputs

### Configuration Tests (`test_config.py`)
Tests configuration management:
- Loading defaults
- Get/set operations
- Persistence
- Config merging

**Key scenarios:**
- Default configuration values
- Nested key access
- File persistence
- Config file merging

### Skills Tests (`test_skills.py`)
Tests skills management system:
- Skill loading from SKILL.md
- Listing available skills
- Installing skills
- Metadata parsing

**Key scenarios:**
- YAML frontmatter parsing
- Skill deduplication
- Multi-file skill installation
- Skill directory hierarchy

### Workflow Tests (`test_workflows.py`)
Tests workflow engine:
- YAML workflow parsing
- Multi-step execution
- Command and agent steps
- Failure handling

**Key scenarios:**
- Workflow with dependencies
- Agent orchestration steps
- Step failure stops execution
- Callback mechanisms

### Context Harness Tests (`test_context_harness.py`)
Tests repository context management:
- File scanning
- Symbol extraction
- Git operations
- File I/O with guardrails

**Key scenarios:**
- Protected path enforcement
- Python/JavaScript symbol extraction
- Context assembly for LLM prompts
- File write protection

### Orchestration Tests (`test_orchestration.py`)
Tests multi-agent orchestration:
- Plan-and-execute cycle
- Event emission
- Code block application
- Self-healing loops

**Key scenarios:**
- Full orchestration flow
- File generation from LLM output
- Sandbox verification
- Error handling

### CLI Tests (`test_cli_commands.py`)
Tests command-line interface:
- Basic commands (help, version, doctor)
- Skill management commands
- Workflow commands
- Error handling

**Key scenarios:**
- CLI subcommands
- Environment variables
- Working directory handling
- Output formatting

## Environment Variables

Tests respect the following environment variables:

- `VADER_PROVIDER` - Default LLM provider
- `VADER_MODEL` - Default model name
- `BASE_URL` - Service base URL (not used in these tests as VADER is CLI-based)

## Test Fixtures

Common fixtures available in `conftest.py`:

- `clean_env` - Clean environment without user configs
- `isolated_workspace` - Temporary isolated workspace
- `sample_skill` - Pre-created sample skill
- `sample_workflow` - Pre-created sample workflow
- `mock_git_repo` - Mock git repository
- `sample_python_project` - Sample Python project structure

## Writing New Tests

### Test Structure
```python
def test_feature_behavior(tmp_path):
    """Test that feature behaves correctly."""
    # Arrange
    component = Component(workspace_dir=str(tmp_path))
    
    # Act
    result = component.do_something()
    
    # Assert
    assert result.success is True
    assert len(result.items) > 0
```

### Using Fixtures
```python
def test_with_sample_skill(sample_skill):
    """Test using pre-created skill fixture."""
    manager = SkillManager()
    skill = manager.load_skill(sample_skill / "SKILL.md")
    assert skill.name == "sample-skill"
```

### Temporary Files
```python
def test_file_operations(tmp_path):
    """Test using temporary directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.read_text() == "content"
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run functional tests
  run: |
    pip install -e .
    pytest tests/functional/ -v --tb=short
```

## Troubleshooting

### Import errors
Ensure VADER is installed: `pip install -e .`

### CLI tests fail
CLI tests require VADER to be installed globally. Skip with: `pytest -m "not cli"`

### Tests timeout
Increase timeout: `pytest --timeout=600`

### Git-related test failures
Some tests require git to be installed and configured.

## Test Coverage

To generate coverage report:

```bash
pytest tests/functional/ --cov=vader --cov-report=html
open htmlcov/index.html
```

## Contributing

When adding new features to VADER:

1. Write functional tests for the new feature
2. Ensure tests follow existing patterns
3. Use appropriate fixtures from `conftest.py`
4. Add test documentation to this README
5. Run full test suite before submitting PR

---

**Generated by TestKraft** - AI-powered test generation platform
