"""
Functional tests for VADER workflow engine.
Tests workflow loading, parsing, execution, and multi-step orchestration.
"""
import pytest
from pathlib import Path
from vader.workflows.engine import WorkflowEngine, Workflow, WorkflowStep


class TestWorkflowLoading:
    """Test workflow loading from YAML files."""

    def test_load_simple_workflow(self, tmp_path):
        """Test loading a simple workflow with basic steps."""
        workflow_content = """
name: test-workflow
description: A simple test workflow
steps:
  - id: step1
    name: First Step
    type: command
    run: echo "Hello"
  - id: step2
    name: Second Step
    type: command
    run: echo "World"
"""
        workflow_file = tmp_path / "test.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        assert workflow is not None
        assert workflow.name == "test-workflow"
        assert workflow.description == "A simple test workflow"
        assert len(workflow.steps) == 2

    def test_load_workflow_agent_steps(self, tmp_path):
        """Test loading workflow with agent steps."""
        workflow_content = """
name: agent-workflow
steps:
  - id: architect
    name: Plan Architecture
    type: agent
    prompt: "Design the system architecture"
  - id: coder
    name: Implement Code
    type: agent
    prompt: "Write the implementation"
"""
        workflow_file = tmp_path / "agent.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        assert len(workflow.steps) == 2
        assert workflow.steps[0].type == "agent"
        assert workflow.steps[1].type == "agent"
        assert workflow.steps[0].config["prompt"] == "Design the system architecture"

    def test_load_workflow_from_workflows_directory(self, tmp_path):
        """Test loading workflow from workflows subdirectory."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()

        workflow_content = """
name: subdir-workflow
steps:
  - id: test
    name: Test Step
    type: command
    run: echo "test"
"""
        (workflows_dir / "subdir.yaml").write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow("subdir.yaml")

        assert workflow.name == "subdir-workflow"

    def test_load_workflow_from_vader_directory(self, tmp_path):
        """Test loading workflow from .vader/workflows directory."""
        vader_workflows_dir = tmp_path / ".vader" / "workflows"
        vader_workflows_dir.mkdir(parents=True)

        workflow_content = """
name: vader-workflow
steps:
  - id: test
    name: Test Step
    type: command
    run: echo "vader"
"""
        (vader_workflows_dir / "vader.yaml").write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow("vader.yaml")

        assert workflow.name == "vader-workflow"

    def test_load_nonexistent_workflow(self, tmp_path):
        """Test loading nonexistent workflow raises error."""
        engine = WorkflowEngine(workspace_dir=str(tmp_path))

        with pytest.raises(FileNotFoundError):
            engine.load_workflow("nonexistent.yaml")

    def test_load_workflow_without_steps(self, tmp_path):
        """Test loading workflow without steps."""
        workflow_content = """
name: empty-workflow
description: Workflow with no steps
"""
        workflow_file = tmp_path / "empty.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        assert workflow.name == "empty-workflow"
        assert len(workflow.steps) == 0

    def test_load_workflow_minimal_step_config(self, tmp_path):
        """Test loading workflow with minimal step configuration."""
        workflow_content = """
name: minimal-workflow
steps:
  - type: command
"""
        workflow_file = tmp_path / "minimal.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        assert len(workflow.steps) == 1
        assert workflow.steps[0].type == "command"
        assert workflow.steps[0].name == "Unnamed Step"  # Default name


class TestWorkflowSteps:
    """Test workflow step parsing and properties."""

    def test_workflow_step_command_type(self, tmp_path):
        """Test command-type workflow step."""
        workflow_content = """
name: command-workflow
steps:
  - id: cmd_step
    name: Command Step
    type: command
    run: echo "test"
    timeout: 30
"""
        workflow_file = tmp_path / "command.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        step = workflow.steps[0]
        assert step.id == "cmd_step"
        assert step.name == "Command Step"
        assert step.type == "command"
        assert step.config["run"] == "echo \"test\""
        assert step.config["timeout"] == 30

    def test_workflow_step_agent_type(self, tmp_path):
        """Test agent-type workflow step."""
        workflow_content = """
name: agent-workflow
steps:
  - id: agent_step
    name: Agent Step
    type: agent
    prompt: "Generate code for authentication"
    model: "custom-model"
"""
        workflow_file = tmp_path / "agent.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        step = workflow.steps[0]
        assert step.id == "agent_step"
        assert step.type == "agent"
        assert step.config["prompt"] == "Generate code for authentication"
        assert step.config["model"] == "custom-model"

    def test_workflow_multiple_step_types(self, tmp_path):
        """Test workflow with multiple step types."""
        workflow_content = """
name: mixed-workflow
steps:
  - id: cmd1
    type: command
    run: echo "start"
  - id: agent1
    type: agent
    prompt: "Generate code"
  - id: cmd2
    type: command
    run: echo "end"
"""
        workflow_file = tmp_path / "mixed.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        assert len(workflow.steps) == 3
        assert workflow.steps[0].type == "command"
        assert workflow.steps[1].type == "agent"
        assert workflow.steps[2].type == "command"


class TestWorkflowExecution:
    """Test workflow execution."""

    def test_execute_simple_command_workflow(self, tmp_path, monkeypatch):
        """Test executing workflow with simple commands."""
        # Create test file to verify execution
        test_file = tmp_path / "output.txt"

        workflow_content = f"""
name: simple-execution
steps:
  - id: write_file
    name: Write Test File
    type: command
    run: echo "test output" > {test_file}
"""
        workflow_file = tmp_path / "simple.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        # Mock the provider to avoid actual LLM calls
        from vader.providers.mock import MockProvider
        monkeypatch.setattr("vader.workflows.engine.VaderEngine.__init__",
                            lambda self, workspace_dir: setattr(self, 'provider', MockProvider()))

        success = engine.execute(workflow)

        assert success is True
        assert test_file.exists()
        assert "test output" in test_file.read_text()

    def test_execute_workflow_with_callback(self, tmp_path):
        """Test workflow execution with step update callback."""
        workflow_content = """
name: callback-workflow
steps:
  - id: step1
    name: First
    type: command
    run: echo "first"
  - id: step2
    name: Second
    type: command
    run: echo "second"
"""
        workflow_file = tmp_path / "callback.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        # Track callback invocations
        callbacks = []

        def on_step_update(step, status):
            callbacks.append((step.id, status))

        engine.execute(workflow, on_step_update=on_step_update)

        # Should have callbacks for each step
        assert len(callbacks) >= 2
        assert any(step_id == "step1" for step_id, _ in callbacks)
        assert any(step_id == "step2" for step_id, _ in callbacks)

    def test_execute_workflow_step_failure(self, tmp_path):
        """Test workflow execution stops on step failure."""
        workflow_content = """
name: failure-workflow
steps:
  - id: success_step
    name: Success
    type: command
    run: echo "success"
  - id: failure_step
    name: Failure
    type: command
    run: exit 1
  - id: never_reached
    name: Never Reached
    type: command
    run: echo "unreachable"
"""
        workflow_file = tmp_path / "failure.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        success = engine.execute(workflow)

        assert success is False

    def test_execute_empty_workflow(self, tmp_path):
        """Test executing workflow with no steps."""
        workflow_content = """
name: empty-workflow
steps: []
"""
        workflow_file = tmp_path / "empty.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        success = engine.execute(workflow)

        # Empty workflow should succeed
        assert success is True


class TestWorkflowObject:
    """Test Workflow and WorkflowStep objects."""

    def test_workflow_step_object_creation(self):
        """Test WorkflowStep object creation."""
        config = {
            "id": "test_id",
            "name": "Test Step",
            "type": "command",
            "run": "echo test"
        }

        step = WorkflowStep(
            id="test_id",
            name="Test Step",
            type="command",
            config=config
        )

        assert step.id == "test_id"
        assert step.name == "Test Step"
        assert step.type == "command"
        assert step.config == config

    def test_workflow_object_creation(self):
        """Test Workflow object creation."""
        steps = [
            WorkflowStep("step1", "First", "command", {}),
            WorkflowStep("step2", "Second", "agent", {})
        ]

        workflow = Workflow(
            name="test-workflow",
            description="Test description",
            steps=steps
        )

        assert workflow.name == "test-workflow"
        assert workflow.description == "Test description"
        assert len(workflow.steps) == 2
        assert workflow.steps[0].id == "step1"
        assert workflow.steps[1].id == "step2"


class TestWorkflowComplexScenarios:
    """Test complex workflow scenarios."""

    def test_workflow_with_dependencies(self, tmp_path):
        """Test workflow with step dependencies."""
        output_file1 = tmp_path / "step1.txt"
        output_file2 = tmp_path / "step2.txt"

        workflow_content = f"""
name: dependency-workflow
steps:
  - id: create_base
    name: Create Base File
    type: command
    run: echo "base" > {output_file1}
  - id: use_base
    name: Use Base File
    type: command
    run: cat {output_file1} && echo "derived" > {output_file2}
"""
        workflow_file = tmp_path / "dependency.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        success = engine.execute(workflow)

        assert success is True
        assert output_file1.exists()
        assert output_file2.exists()
        assert "base" in output_file1.read_text()
        assert "derived" in output_file2.read_text()

    def test_workflow_name_from_filename(self, tmp_path):
        """Test workflow name defaults to filename if not specified."""
        workflow_content = """
steps:
  - id: test
    type: command
    run: echo "test"
"""
        workflow_file = tmp_path / "custom-name.yaml"
        workflow_file.write_text(workflow_content)

        engine = WorkflowEngine(workspace_dir=str(tmp_path))
        workflow = engine.load_workflow(str(workflow_file))

        # Should use filename without extension as name
        assert workflow.name == "custom-name"
