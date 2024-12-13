import pytest
import os
from shell_emulator.shell import ShellEmulator

class TestBasicFunctionality:
    @pytest.fixture
    def shell(self):
        config_path = os.path.join(os.path.dirname(__file__), '../shell_emulator/config.xml')
        return ShellEmulator(config_path)

    def test_initial_directory(self, shell):
        """Test that shell starts in root directory"""
        assert shell.current_dir == "/"
        assert shell.ls() == ""  # Empty root directory at start

    def test_command_logging(self, shell, tmp_path):
        """Test that commands are properly logged"""
        # Set up a temporary log file
        shell.config['log_file'] = str(tmp_path / "test_log.csv")
        
        # Execute some commands
        shell.echo(["test message"])
        shell.ls()
        
        # Check log file exists and contains entries
        assert os.path.exists(shell.config['log_file'])
        with open(shell.config['log_file'], 'r') as f:
            log_content = f.read()
            assert "test message" in log_content
            assert "ls" in log_content

    def test_filesystem_operations(self, shell):
        """Test basic filesystem operations"""
        # Create a test directory structure
        shell.fs_content['/testdir'] = {'type': 'dir', 'size': 0}
        shell.fs_content['/testdir/file.txt'] = {'type': 'file', 'size': 10}
        
        # Test directory navigation
        shell.cd(['testdir'])
        assert shell.current_dir == '/testdir'
        
        # Test directory listing
        ls_result = shell.ls()
        assert 'file.txt' in ls_result
        
        # Test directory removal (should fail as directory is not empty)
        shell.rmdir(['testdir'])
        assert '/testdir' in shell.fs_content  # Directory should still exist
