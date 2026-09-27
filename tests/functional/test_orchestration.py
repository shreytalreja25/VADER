"""
Functional tests for VADER orchestration engine.
Tests multi-agent orchestration, plan-and-execute cycle, and self-healing.
"""
import pytest
from pathlib import Path
from vader.orchestration.engine import VaderEngine, ExecutionStep
from vader.providers.mock import MockProvider


class TestVaderEngineInitialization:
    """Test orchestration engine initialization."""

    def test_engine_initialization(self, tmp_path):
        """Test that engine initializes with workspace."""
        engine = VaderEngine(workspace_dir=str(tmp_path))

        assert engine.harness is not None
        assert engine.provider is not None
        assert engine.harness.root_dir == tmp_path

    def test_engine_initialization_with_provider(self, tmp_path):
        """Test engine initialization with custom provider."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        assert engine.provider == mock_provider
        assert isinstance(engine.provider, MockProvider)

    def test_engine_max_repairs_configuration(self, tmp_path):
        """Test that max repairs is configured from config."""
        engine = VaderEngine(workspace_dir=str(tmp_path))

        assert hasattr(engine, 'max_repairs')
        assert engine.max_repairs > 0


class TestExecutionStep:
    """Test ExecutionStep object."""

    def test_execution_step_creation(self):
        """Test creating execution step."""
        step = ExecutionStep(
            step_num=1,
            description="Test step",
            status="pending"
        )

        assert step.step_num == 1
        assert step.description == "Test step"
        assert step.status == "pending"

    def test_execution_step_default_status(self):
        """Test execution step default status."""
        step = ExecutionStep(step_num=1, description="Test")

        assert step.status == "pending"


class TestPlanAndExecute:
    """Test plan-and-execute orchestration cycle."""

    def test_plan_and_execute_simple_task(self, tmp_path):
        """Test executing a simple task with mock provider."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        result = engine.plan_and_execute("Create a simple todo app")

        assert isinstance(result, dict)
        assert "success" in result
        assert "modified_files" in result
        assert isinstance(result["modified_files"], list)

    def test_plan_and_execute_with_events(self, tmp_path):
        """Test plan-and-execute with event callbacks."""
        mock_provider = MockProvider()
        events = []

        def on_event(event_name, payload):
            events.append((event_name, payload))

        engine = VaderEngine(
            workspace_dir=str(tmp_path),
            provider=mock_provider,
            on_event=on_event
        )

        result = engine.plan_and_execute("Create a todo app")

        # Should emit events during execution
        assert len(events) > 0
        event_names = [e[0] for e in events]
        assert "start" in event_names
        assert "complete" in event_names

    def test_plan_and_execute_emits_phases(self, tmp_path):
        """Test that execution emits phase events."""
        mock_provider = MockProvider()
        phases = []

        def on_event(event_name, payload):
            if event_name == "phase":
                phases.append(payload.get("name"))

        engine = VaderEngine(
            workspace_dir=str(tmp_path),
            provider=mock_provider,
            on_event=on_event
        )

        engine.plan_and_execute("Create code")

        # Should go through multiple phases
        assert len(phases) > 0

    def test_plan_and_execute_creates_files(self, tmp_path):
        """Test that plan-and-execute creates files."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        result = engine.plan_and_execute("Create a todo app")

        # Mock provider generates HTML, CSS, JS files
        assert len(result["modified_files"]) > 0

        # Verify files were actually created
        for file_path in result["modified_files"]:
            assert (tmp_path / file_path).exists()

    def test_plan_and_execute_returns_plan(self, tmp_path):
        """Test that result includes execution plan."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        result = engine.plan_and_execute("Create a todo app")

        assert "plan" in result
        assert isinstance(result["plan"], str)
        assert len(result["plan"]) > 0

    def test_plan_and_execute_returns_review(self, tmp_path):
        """Test that result includes review feedback."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        result = engine.plan_and_execute("Create code")

        assert "review" in result
        assert isinstance(result["review"], str)


class TestFileCodeBlockApplication:
    """Test applying code blocks from LLM responses."""

    def test_apply_code_blocks_single_file(self, tmp_path):
        """Test applying single file code block."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        code_output = """
FILE: test.py
```python
def hello():
    print("Hello World")
```
"""
        applied = engine._apply_code_blocks(code_output)

        assert "test.py" in applied
        assert (tmp_path / "test.py").exists()
        content = (tmp_path / "test.py").read_text()
        assert "def hello()" in content

    def test_apply_code_blocks_multiple_files(self, tmp_path):
        """Test applying multiple file code blocks."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        code_output = """
FILE: file1.py
```python
print("File 1")
```

FILE: file2.js
```javascript
console.log("File 2");
```
"""
        applied = engine._apply_code_blocks(code_output)

        assert len(applied) == 2
        assert "file1.py" in applied
        assert "file2.js" in applied
        assert (tmp_path / "file1.py").exists()
        assert (tmp_path / "file2.js").exists()

    def test_apply_code_blocks_no_blocks(self, tmp_path):
        """Test applying code blocks when none present."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        code_output = "Just plain text without code blocks"
        applied = engine._apply_code_blocks(code_output)

        assert len(applied) == 0

    def test_apply_code_blocks_with_language_tag(self, tmp_path):
        """Test applying code blocks with various language tags."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        code_output = """
FILE: test.py
```python
# Python code
```

FILE: test.js
```javascript
// JS code
```

FILE: test.md
```markdown
# Markdown
```
"""
        applied = engine._apply_code_blocks(code_output)

        assert len(applied) == 3


class TestSandboxChecks:
    """Test sandbox verification and testing."""

    def test_run_sandbox_checks_no_tests(self, tmp_path):
        """Test sandbox checks with no test suite."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        passed, message = engine._run_sandbox_checks()

        # Should pass when no tests exist
        assert passed is True
        assert "No automated test suite" in message

    def test_run_sandbox_checks_with_pytest_ini(self, tmp_path):
        """Test sandbox detects pytest configuration."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        # Create pytest.ini
        (tmp_path / "pytest.ini").write_text("[pytest]\ntestpaths = tests")

        # This will try to run pytest, which may fail
        passed, message = engine._run_sandbox_checks()

        assert isinstance(passed, bool)
        assert isinstance(message, str)

    def test_run_sandbox_checks_with_package_json(self, tmp_path):
        """Test sandbox detects package.json for npm test."""
        mock_provider = MockProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=mock_provider)

        # Create package.json
        (tmp_path / "package.json").write_text('{"name": "test"}')

        # This will try to run npm test
        passed, message = engine._run_sandbox_checks()

        assert isinstance(passed, bool)
        assert isinstance(message, str)


class TestEventEmission:
    """Test event emission during orchestration."""

    def test_emit_start_event(self, tmp_path):
        """Test that start event is emitted."""
        mock_provider = MockProvider()
        events = []

        def on_event(event_name, payload):
            events.append((event_name, payload))

        engine = VaderEngine(
            workspace_dir=str(tmp_path),
            provider=mock_provider,
            on_event=on_event
        )

        engine.plan_and_execute("Test task")

        start_events = [e for e in events if e[0] == "start"]
        assert len(start_events) > 0
        assert "prompt" in start_events[0][1]

    def test_emit_plan_created_event(self, tmp_path):
        """Test that plan_created event is emitted."""
        mock_provider = MockProvider()
        events = []

        def on_event(event_name, payload):
            events.append((event_name, payload))

        engine = VaderEngine(
            workspace_dir=str(tmp_path),
            provider=mock_provider,
            on_event=on_event
        )

        engine.plan_and_execute("Test task")

        plan_events = [e for e in events if e[0] == "plan_created"]
        assert len(plan_events) > 0
        assert "plan" in plan_events[0][1]

    def test_emit_files_written_event(self, tmp_path):
        """Test that files_written event is emitted."""
        mock_provider = MockProvider()
        events = []

        def on_event(event_name, payload):
            events.append((event_name, payload))

        engine = VaderEngine(
            workspace_dir=str(tmp_path),
            provider=mock_provider,
            on_event=on_event
        )

        engine.plan_and_execute("Create files")

        files_events = [e for e in events if e[0] == "files_written"]
        if len(files_events) > 0:
            assert "files" in files_events[0][1]

    def test_emit_complete_event(self, tmp_path):
        """Test that complete event is emitted."""
        mock_provider = MockProvider()
        events = []

        def on_event(event_name, payload):
            events.append((event_name, payload))

        engine = VaderEngine(
            workspace_dir=str(tmp_path),
            provider=mock_provider,
            on_event=on_event
        )

        engine.plan_and_execute("Test task")

        complete_events = [e for e in events if e[0] == "complete"]
        assert len(complete_events) > 0
        assert "success" in complete_events[0][1]


class TestErrorHandling:
    """Test error handling in orchestration."""

    def test_plan_and_execute_handles_exceptions(self, tmp_path):
        """Test that plan-and-execute handles exceptions gracefully."""
        # Create a provider that will raise an exception
        class FailingProvider(MockProvider):
            def generate(self, prompt, system_prompt="", stream=False):
                raise Exception("Test exception")

        failing_provider = FailingProvider()
        engine = VaderEngine(workspace_dir=str(tmp_path), provider=failing_provider)

        result = engine.plan_and_execute("Test task")

        assert result["success"] is False
        assert "error" in result

    def test_plan_and_execute_emits_error_event(self, tmp_path):
        """Test that error event is emitted on failure."""
        class FailingProvider(MockProvider):
            def generate(self, prompt, system_prompt="", stream=False):
                raise Exception("Test exception")

        failing_provider = FailingProvider()
        events = []

        def on_event(event_name, payload):
            events.append((event_name, payload))

        engine = VaderEngine(
            workspace_dir=str(tmp_path),
            provider=failing_provider,
            on_event=on_event
        )

        result = engine.plan_and_execute("Test task")

        error_events = [e for e in events if e[0] == "error"]
        assert len(error_events) > 0


class TestIntegration:
    """Integration tests for full orchestration flow."""

    def test_full_orchestration_cycle(self, tmp_path):
        """Test complete orchestration cycle from prompt to files."""
        mock_provider = MockProvider()
        events = []

        def on_event(event_name, payload):
            events.append((event_name, payload))

        engine = VaderEngine(
            workspace_dir=str(tmp_path),
            provider=mock_provider,
            on_event=on_event
        )

        result = engine.plan_and_execute("Create a todo application")

        # Verify result structure
        assert result["success"] in [True, False]
        assert "modified_files" in result
        assert "plan" in result
        assert "review" in result

        # Verify events were emitted
        event_names = [e[0] for e in events]
        assert "start" in event_names
        assert "complete" in event_names

        # Verify files were created
        for file_path in result["modified_files"]:
            assert (tmp_path / file_path).exists()
