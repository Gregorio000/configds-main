import os
import sys
import tarfile
import csv
from datetime import datetime
import xml.etree.ElementTree as ET
import time

class ShellEmulator:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.current_dir = "/"
        self.start_time = time.time()
        self.fs_content = {}
        self._load_filesystem()
        
    def _load_config(self, config_path):
        tree = ET.parse(config_path)
        root = tree.getroot()
        return {
            'hostname': root.find('hostname').text,
            'filesystem_archive': root.find('filesystem_archive').text,
            'log_file': root.find('log_file').text
        }
        
    def _load_filesystem(self):
        try:
            with tarfile.open(self.config['filesystem_archive'], 'r') as tar:
                for member in tar.getmembers():
                    self.fs_content[member.name] = {
                        'type': 'dir' if member.isdir() else 'file',
                        'size': member.size
                    }
        except FileNotFoundError:
            self.fs_content['/'] = {'type': 'dir', 'size': 0}
            
    def _log_action(self, command):
        with open(self.config['log_file'], 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), command])
            
    def ls(self, args=None):
        target_dir = self.current_dir
        if args:
            target_dir = os.path.normpath(os.path.join(self.current_dir, args[0]))
            
        items = []
        for path in self.fs_content:
            if os.path.dirname(path) == target_dir.rstrip('/'):
                items.append(os.path.basename(path))
        return ' '.join(sorted(items)) if items else ''
        
    def cd(self, args):
        if not args or args[0] == '~':
            self.current_dir = '/'
            return
            
        new_path = os.path.normpath(os.path.join(self.current_dir, args[0]))
        if new_path in self.fs_content and self.fs_content[new_path]['type'] == 'dir':
            self.current_dir = new_path
        else:
            print(f"cd: {args[0]}: No such directory")
            
    def echo(self, args):
        return ' '.join(args) if args else ''
        
    def rmdir(self, args):
        if not args:
            print("rmdir: missing operand")
            return
            
        target_dir = os.path.normpath(os.path.join(self.current_dir, args[0]))
        if target_dir in self.fs_content:
            if self.fs_content[target_dir]['type'] == 'dir':
                # Check if directory is empty
                for path in self.fs_content:
                    if path.startswith(target_dir + '/'):
                        print(f"rmdir: failed to remove '{args[0]}': Directory not empty")
                        return
                del self.fs_content[target_dir]
            else:
                print(f"rmdir: failed to remove '{args[0]}': Not a directory")
        else:
            print(f"rmdir: failed to remove '{args[0]}': No such file or directory")
            
    def uptime(self, args=None):
        uptime_seconds = time.time() - self.start_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"up {hours}:{minutes:02d}"
        
    def run(self):
        while True:
            try:
                prompt = f"{self.config['hostname']}:{self.current_dir}$ "
                command = input(prompt).strip()
                
                if not command:
                    continue
                    
                self._log_action(command)
                
                parts = command.split()
                cmd, args = parts[0], parts[1:] if len(parts) > 1 else []
                
                if cmd == 'exit':
                    break
                elif cmd in ['ls', 'cd', 'echo', 'rmdir', 'uptime']:
                    result = getattr(self, cmd)(args)
                    if result is not None:
                        print(result)
                else:
                    print(f"Command not found: {cmd}")
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit the emulator")
            except Exception as e:
                print(f"Error: {str(e)}")
                
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python shell.py <config_file>")
        sys.exit(1)
        
    emulator = ShellEmulator(sys.argv[1])
    emulator.run()
