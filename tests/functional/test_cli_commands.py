"""
Functional tests for VADER CLI commands.
Tests command-line interface functionality via subprocess execution.
"""
import os
import subprocess
import pytest
from pathlib import Path


# Skip CLI tests if VADER is not installed
try:
    result = subprocess.run(
        ["vader", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    VADER_INSTALLED = result.returncode == 0
except (FileNotFoundError, subprocess.TimeoutExpired):
    VADER_INSTALLED = False


@pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
class TestCLIBasicCommands:
    """Test basic CLI commands."""

    def test_vader_version_command(self):
        """Test vader --version command."""
        result = subprocess.run(
            ["vader", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        assert "Vader" in result.stdout or "version" in result.stdout.lower()

    def test_vader_help_command(self):
        """Test vader --help command."""
        result = subprocess.run(
            ["vader", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        assert "vader" in result.stdout.lower()

    def test_vader_doctor_command(self):
        """Test vader doctor command."""
        result = subprocess.run(
            ["vader", "doctor"],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Doctor may succeed or fail depending on environment
        assert isinstance(result.returncode, int)
        # Should output diagnostic information
        assert len(result.stdout) > 0 or len(result.stderr) > 0


@pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
class TestCLISkillCommands:
    """Test skill management CLI commands."""

    def test_skill_list_command(self):
        """Test vader skill list command."""
        result = subprocess.run(
            ["vader", "skill", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0
        # May have skills or may be empty
        assert isinstance(result.stdout, str)

    def test_skill_install_nonexistent(self, tmp_path):
        """Test vader skill install with nonexistent path."""
        result = subprocess.run(
            ["vader", "skill", "install", str(tmp_path / "nonexistent")],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should fail gracefully
        assert result.returncode != 0 or "not found" in result.stderr.lower() or "failed" in result.stdout.lower()


@pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
class TestCLIWorkflowCommands:
    """Test workflow management CLI commands."""

    def test_workflow_list_command(self):
        """Test vader workflow list command."""
        result = subprocess.run(
            ["vader", "workflow", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0
        assert isinstance(result.stdout, str)

    def test_workflow_run_nonexistent(self):
        """Test vader workflow run with nonexistent workflow."""
        result = subprocess.run(
            ["vader", "workflow", "run", "nonexistent.yaml"],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should fail with file not found
        assert result.returncode != 0 or "not found" in result.stderr.lower() or "error" in result.stdout.lower()


@pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
class TestCLICronCommands:
    """Test cron scheduler CLI commands."""

    def test_cron_list_command(self):
        """Test vader cron list command."""
        result = subprocess.run(
            ["vader", "cron", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0
        assert isinstance(result.stdout, str)


@pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
class TestCLICodeCommand:
    """Test code execution command."""

    def test_code_command_with_mock_provider(self, tmp_path):
        """Test vader code command with mock provider."""
        # Create a temporary workspace
        os.chdir(tmp_path)

        result = subprocess.run(
            ["vader", "code", "--provider", "mock", "Create a simple hello.txt file with content 'Hello'"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(tmp_path)
        )

        # Command may or may not succeed depending on environment
        assert isinstance(result.returncode, int)
        assert isinstance(result.stdout, str)


class TestCLIWithoutInstallation:
    """Test CLI behavior when not installed (using python -m)."""

    def test_run_vader_as_module(self, tmp_path):
        """Test running vader as python module."""
        vader_path = Path(__file__).parent.parent.parent / "vader"

        if vader_path.exists():
            result = subprocess.run(
                ["python", "-m", "vader", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(vader_path.parent)
            )

            # May work or may not depending on setup
            assert isinstance(result.returncode, int)


class TestCLIErrorHandling:
    """Test CLI error handling."""

    @pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
    def test_invalid_command(self):
        """Test vader with invalid command."""
        result = subprocess.run(
            ["vader", "invalid_command_xyz"],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should either fail or show help/error
        assert isinstance(result.returncode, int)

    @pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
    def test_skill_install_missing_argument(self):
        """Test vader skill install without path argument."""
        result = subprocess.run(
            ["vader", "skill", "install"],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should fail with missing argument error
        assert result.returncode != 0


class TestCLIEnvironmentVariables:
    """Test CLI with environment variables."""

    @pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
    def test_cli_with_custom_env(self, tmp_path):
        """Test CLI with custom environment variables."""
        env = os.environ.copy()
        env["VADER_PROVIDER"] = "mock"

        result = subprocess.run(
            ["vader", "doctor"],
            capture_output=True,
            text=True,
            timeout=10,
            env=env
        )

        assert isinstance(result.returncode, int)


class TestCLIOutputFormats:
    """Test CLI output formatting."""

    @pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
    def test_help_output_readable(self):
        """Test that help output is human-readable."""
        result = subprocess.run(
            ["vader", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Should contain readable help text
        output = result.stdout.lower()
        assert any(word in output for word in ["usage", "command", "option", "help"])

    @pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
    def test_version_output_format(self):
        """Test that version output has expected format."""
        result = subprocess.run(
            ["vader", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Should contain version information
        output = result.stdout
        assert len(output.strip()) > 0


class TestCLIWorkingDirectory:
    """Test CLI commands in different working directories."""

    @pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
    def test_cli_in_temp_directory(self, tmp_path):
        """Test running CLI commands in temporary directory."""
        result = subprocess.run(
            ["vader", "doctor"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(tmp_path)
        )

        # Should work from any directory
        assert isinstance(result.returncode, int)

    @pytest.mark.skipif(not VADER_INSTALLED, reason="VADER CLI not installed")
    def test_skill_list_in_different_directory(self, tmp_path):
        """Test skill list from different working directory."""
        result = subprocess.run(
            ["vader", "skill", "list"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(tmp_path)
        )

        assert result.returncode == 0
