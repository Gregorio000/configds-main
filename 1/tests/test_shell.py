import pytest
import os
import time
from shell_emulator.shell import ShellEmulator

@pytest.fixture
def shell():
    config_path = os.path.join(os.path.dirname(__file__), '../shell_emulator/config.xml')
    return ShellEmulator(config_path)

class TestLsCommand:
    def test_ls_empty_directory(self, shell):
        assert shell.ls() == ''

    def test_ls_with_files(self, shell):
        shell.fs_content['/test.txt'] = {'type': 'file', 'size': 0}
        assert 'test.txt' in shell.ls()

    def test_ls_with_subdirectory(self, shell):
        shell.fs_content['/testdir'] = {'type': 'dir', 'size': 0}
        assert 'testdir' in shell.ls()

class TestCdCommand:
    def test_cd_to_root(self, shell):
        shell.cd(['~'])
        assert shell.current_dir == '/'

    def test_cd_to_valid_directory(self, shell):
        shell.fs_content['/testdir'] = {'type': 'dir', 'size': 0}
        shell.cd(['testdir'])
        assert shell.current_dir == '/testdir'

    def test_cd_to_invalid_directory(self, shell, capsys):
        shell.cd(['nonexistent'])
        captured = capsys.readouterr()
        assert "No such directory" in captured.out

class TestEchoCommand:
    def test_echo_empty(self, shell):
        assert shell.echo([]) == ''

    def test_echo_single_word(self, shell):
        assert shell.echo(['hello']) == 'hello'

    def test_echo_multiple_words(self, shell):
        assert shell.echo(['hello', 'world']) == 'hello world'

class TestRmdirCommand:
    def test_rmdir_empty_directory(self, shell, capsys):
        shell.fs_content['/testdir'] = {'type': 'dir', 'size': 0}
        shell.rmdir(['testdir'])
        assert '/testdir' not in shell.fs_content

    def test_rmdir_non_empty_directory(self, shell, capsys):
        shell.fs_content['/testdir'] = {'type': 'dir', 'size': 0}
        shell.fs_content['/testdir/file.txt'] = {'type': 'file', 'size': 0}
        shell.rmdir(['testdir'])
        captured = capsys.readouterr()
        assert "Directory not empty" in captured.out

    def test_rmdir_nonexistent_directory(self, shell, capsys):
        shell.rmdir(['nonexistent'])
        captured = capsys.readouterr()
        assert "No such file or directory" in captured.out

class TestUptimeCommand:
    def test_uptime_format(self, shell):
        result = shell.uptime()
        assert ':' in result
        assert 'up' in result

    def test_uptime_increases(self, shell):
        first = shell.uptime()
        time.sleep(1)
        second = shell.uptime()
        assert first != second

    def test_uptime_zero_start(self, shell):
        # This test assumes the shell was just created
        result = shell.uptime()
        assert 'up 0:' in result
