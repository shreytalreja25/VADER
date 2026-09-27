"""
Functional tests for VADER context harness.
Tests repository scanning, symbol extraction, git operations, and file I/O.
"""
import pytest
from pathlib import Path
from vader.context.harness import ContextHarness


class TestContextHarnessInitialization:
    """Test context harness initialization."""

    def test_harness_initialization(self, tmp_path):
        """Test that harness initializes with workspace directory."""
        harness = ContextHarness(root_dir=str(tmp_path))

        assert harness.root_dir == tmp_path
        assert isinstance(harness.protected_paths, list)
        assert ".git" in harness.protected_paths

    def test_harness_default_protected_paths(self, tmp_path):
        """Test that default protected paths are configured."""
        harness = ContextHarness(root_dir=str(tmp_path))

        assert ".git" in harness.protected_paths
        assert ".env" in harness.protected_paths
        assert "node_modules" in harness.protected_paths


class TestRepositoryScanning:
    """Test repository file scanning functionality."""

    def test_scan_empty_repository(self, tmp_path):
        """Test scanning empty repository."""
        harness = ContextHarness(root_dir=str(tmp_path))
        files = harness.scan_repository()

        assert isinstance(files, list)
        assert len(files) == 0

    def test_scan_repository_with_files(self, tmp_path):
        """Test scanning repository with source files."""
        # Create test files
        (tmp_path / "file1.py").write_text("print('hello')")
        (tmp_path / "file2.js").write_text("console.log('world');")
        (tmp_path / "file3.txt").write_text("readme content")

        harness = ContextHarness(root_dir=str(tmp_path))
        files = harness.scan_repository()

        assert len(files) == 3
        file_paths = [f["path"] for f in files]
        assert "file1.py" in file_paths
        assert "file2.js" in file_paths
        assert "file3.txt" in file_paths

    def test_scan_repository_excludes_protected_paths(self, tmp_path):
        """Test that protected paths are excluded from scan."""
        # Create files in protected directories
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git config")

        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.js").write_text("module")

        # Create normal file
        (tmp_path / "main.py").write_text("code")

        harness = ContextHarness(root_dir=str(tmp_path))
        files = harness.scan_repository()

        file_paths = [f["path"] for f in files]
        assert "main.py" in file_paths
        assert not any(".git" in path for path in file_paths)
        assert not any("node_modules" in path for path in file_paths)

    def test_scan_repository_nested_directories(self, tmp_path):
        """Test scanning nested directory structure."""
        # Create nested structure
        src_dir = tmp_path / "src" / "components"
        src_dir.mkdir(parents=True)

        (src_dir / "component.js").write_text("export default Component;")
        (tmp_path / "src" / "index.js").write_text("import Component;")
        (tmp_path / "README.md").write_text("# Project")

        harness = ContextHarness(root_dir=str(tmp_path))
        files = harness.scan_repository()

        assert len(files) == 3
        file_paths = [f["path"] for f in files]
        assert any("components" in path for path in file_paths)

    def test_scan_repository_max_files_limit(self, tmp_path):
        """Test that repository scan respects max_files limit."""
        # Create many files
        for i in range(200):
            (tmp_path / f"file_{i}.txt").write_text(f"content {i}")

        harness = ContextHarness(root_dir=str(tmp_path))
        files = harness.scan_repository(max_files=50)

        assert len(files) <= 50

    def test_scan_repository_file_metadata(self, tmp_path):
        """Test that scanned files include metadata."""
        (tmp_path / "test.py").write_text("print('test')")

        harness = ContextHarness(root_dir=str(tmp_path))
        files = harness.scan_repository()

        assert len(files) == 1
        file_info = files[0]

        assert "path" in file_info
        assert "size" in file_info
        assert "extension" in file_info
        assert file_info["extension"] == ".py"
        assert file_info["size"] > 0


class TestSymbolExtraction:
    """Test symbol extraction from source files."""

    def test_extract_symbols_python_functions(self, tmp_path):
        """Test extracting Python function definitions."""
        python_file = tmp_path / "module.py"
        python_file.write_text("""
def function_one():
    pass

def function_two(arg):
    return arg

class MyClass:
    def method(self):
        pass
""")

        harness = ContextHarness(root_dir=str(tmp_path))
        symbols = harness.extract_symbols("module.py")

        assert len(symbols) >= 3
        symbol_names = [s["name"] for s in symbols]
        assert "function_one" in symbol_names
        assert "function_two" in symbol_names
        assert "MyClass" in symbol_names

    def test_extract_symbols_python_classes(self, tmp_path):
        """Test extracting Python class definitions."""
        python_file = tmp_path / "classes.py"
        python_file.write_text("""
class BaseClass:
    pass

class DerivedClass(BaseClass):
    def __init__(self):
        pass
""")

        harness = ContextHarness(root_dir=str(tmp_path))
        symbols = harness.extract_symbols("classes.py")

        class_symbols = [s for s in symbols if s["type"] == "class"]
        assert len(class_symbols) >= 2
        class_names = [s["name"] for s in class_symbols]
        assert "BaseClass" in class_names
        assert "DerivedClass" in class_names

    def test_extract_symbols_javascript(self, tmp_path):
        """Test extracting JavaScript symbols."""
        js_file = tmp_path / "app.js"
        js_file.write_text("""
function myFunction() {
    return true;
}

const myConst = 42;

class MyClass {
    constructor() {}
}

export function exportedFunction() {}
""")

        harness = ContextHarness(root_dir=str(tmp_path))
        symbols = harness.extract_symbols("app.js")

        assert len(symbols) > 0
        symbol_names = [s["name"] for s in symbols]
        assert "myFunction" in symbol_names or "myConst" in symbol_names

    def test_extract_symbols_with_line_numbers(self, tmp_path):
        """Test that extracted symbols include line numbers."""
        python_file = tmp_path / "numbered.py"
        python_file.write_text("""# Line 1: Comment
def first_function():  # Line 2
    pass

def second_function():  # Line 5
    pass
""")

        harness = ContextHarness(root_dir=str(tmp_path))
        symbols = harness.extract_symbols("numbered.py")

        for symbol in symbols:
            assert "line" in symbol
            assert symbol["line"] > 0

    def test_extract_symbols_nonexistent_file(self, tmp_path):
        """Test extracting symbols from nonexistent file."""
        harness = ContextHarness(root_dir=str(tmp_path))
        symbols = harness.extract_symbols("nonexistent.py")

        assert isinstance(symbols, list)
        assert len(symbols) == 0

    def test_extract_symbols_empty_file(self, tmp_path):
        """Test extracting symbols from empty file."""
        (tmp_path / "empty.py").write_text("")

        harness = ContextHarness(root_dir=str(tmp_path))
        symbols = harness.extract_symbols("empty.py")

        assert isinstance(symbols, list)
        assert len(symbols) == 0


class TestFileOperations:
    """Test file reading and writing operations."""

    def test_read_existing_file(self, tmp_path):
        """Test reading existing file."""
        test_file = tmp_path / "test.txt"
        test_content = "Test file content"
        test_file.write_text(test_content)

        harness = ContextHarness(root_dir=str(tmp_path))
        content = harness.read_file("test.txt")

        assert content == test_content

    def test_read_nonexistent_file(self, tmp_path):
        """Test reading nonexistent file returns None."""
        harness = ContextHarness(root_dir=str(tmp_path))
        content = harness.read_file("nonexistent.txt")

        assert content is None

    def test_write_file(self, tmp_path):
        """Test writing file."""
        harness = ContextHarness(root_dir=str(tmp_path))
        content = "New file content"

        harness.write_file("output.txt", content)

        output_file = tmp_path / "output.txt"
        assert output_file.exists()
        assert output_file.read_text() == content

    def test_write_file_creates_directories(self, tmp_path):
        """Test that write_file creates parent directories."""
        harness = ContextHarness(root_dir=str(tmp_path))

        harness.write_file("nested/dir/file.txt", "content")

        nested_file = tmp_path / "nested" / "dir" / "file.txt"
        assert nested_file.exists()
        assert nested_file.read_text() == "content"

    def test_write_file_overwrites_existing(self, tmp_path):
        """Test that write_file overwrites existing file."""
        test_file = tmp_path / "existing.txt"
        test_file.write_text("old content")

        harness = ContextHarness(root_dir=str(tmp_path))
        harness.write_file("existing.txt", "new content")

        assert test_file.read_text() == "new content"

    def test_write_protected_path_raises_error(self, tmp_path):
        """Test that writing to protected path raises PermissionError."""
        harness = ContextHarness(root_dir=str(tmp_path))

        with pytest.raises(PermissionError):
            harness.write_file(".git/config", "malicious")

        with pytest.raises(PermissionError):
            harness.write_file(".env", "SECRET=value")


class TestGitOperations:
    """Test git integration operations."""

    def test_get_git_diff_no_repository(self, tmp_path):
        """Test git diff with no repository returns empty string."""
        harness = ContextHarness(root_dir=str(tmp_path))
        diff = harness.get_git_diff()

        assert isinstance(diff, str)
        assert diff == ""

    def test_get_git_status_no_repository(self, tmp_path):
        """Test git status with no repository returns empty string."""
        harness = ContextHarness(root_dir=str(tmp_path))
        status = harness.get_git_status()

        assert isinstance(status, str)
        assert status == ""

    def test_read_file_unicode_content(self, tmp_path):
        """Test reading file with unicode content."""
        test_file = tmp_path / "unicode.txt"
        unicode_content = "Hello 世界 🚀"
        test_file.write_text(unicode_content, encoding="utf-8")

        harness = ContextHarness(root_dir=str(tmp_path))
        content = harness.read_file("unicode.txt")

        assert content == unicode_content


class TestContextAssembly:
    """Test context assembly for LLM prompts."""

    def test_assemble_context_basic(self, tmp_path):
        """Test basic context assembly."""
        (tmp_path / "main.py").write_text("print('hello')")

        harness = ContextHarness(root_dir=str(tmp_path))
        context = harness.assemble_context()

        assert isinstance(context, str)
        assert "Repository File Tree:" in context
        assert "main.py" in context

    def test_assemble_context_with_relevant_files(self, tmp_path):
        """Test context assembly with relevant files."""
        (tmp_path / "file1.py").write_text("def func1(): pass")
        (tmp_path / "file2.py").write_text("def func2(): pass")

        harness = ContextHarness(root_dir=str(tmp_path))
        context = harness.assemble_context(relevant_files=["file1.py"])

        assert "file1.py" in context
        assert "def func1()" in context

    def test_assemble_context_truncates_long_files(self, tmp_path):
        """Test that context assembly truncates long files."""
        long_content = "x" * 10000  # Very long file
        (tmp_path / "long.py").write_text(long_content)

        harness = ContextHarness(root_dir=str(tmp_path))
        context = harness.assemble_context(relevant_files=["long.py"])

        # Should be truncated to ~3000 characters
        assert len(context) < 5000

    def test_assemble_context_empty_repository(self, tmp_path):
        """Test context assembly for empty repository."""
        harness = ContextHarness(root_dir=str(tmp_path))
        context = harness.assemble_context()

        assert isinstance(context, str)
        assert "Repository File Tree:" in context


class TestProtectedPaths:
    """Test protected path enforcement."""

    def test_is_ignored_protected_paths(self, tmp_path):
        """Test that protected paths are correctly identified."""
        harness = ContextHarness(root_dir=str(tmp_path))

        assert harness.is_ignored(tmp_path / ".git")
        assert harness.is_ignored(tmp_path / ".env")
        assert harness.is_ignored(tmp_path / "node_modules")
        assert harness.is_ignored(tmp_path / "venv")

    def test_is_ignored_normal_paths(self, tmp_path):
        """Test that normal paths are not ignored."""
        harness = ContextHarness(root_dir=str(tmp_path))

        assert not harness.is_ignored(tmp_path / "src")
        assert not harness.is_ignored(tmp_path / "main.py")
        assert not harness.is_ignored(tmp_path / "README.md")

    def test_is_ignored_nested_protected_paths(self, tmp_path):
        """Test that nested protected paths are ignored."""
        harness = ContextHarness(root_dir=str(tmp_path))

        assert harness.is_ignored(tmp_path / ".git" / "objects")
        assert harness.is_ignored(tmp_path / "node_modules" / "package")
