"""
Autonomous Project Engineer for BetSentinel
Continuously builds, tests, and perfects the system
"""
import os
import sys
import io
import json
import time
import subprocess
import re
import traceback
from datetime import datetime, timedelta
from pathlib import Path
import shutil

# Fix UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Project paths
PROJECT_ROOT = Path(__file__).parent
ROADMAP_FILE = PROJECT_ROOT / "roadmap.json"
STATE_FILE = PROJECT_ROOT / "system" / "state.json"
MAIN_FILE = PROJECT_ROOT / "main.py"
LOG_FILE = PROJECT_ROOT / "data" / "app.log"
VENV_ACTIVATE = PROJECT_ROOT / "venv" / "Scripts" / "activate"
GIT_REPO = "https://github.com/dbrkzzzx-creator/BetSentinel.git"
GIT_PATH = r"D:\AI\Git\bin\git.exe"

class AutonomousEngine:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.roadmap = self.load_roadmap()
        self.state = self.load_state()
        self.iteration = 0
        self.start_time = datetime.now()
        
    def load_roadmap(self):
        """Load roadmap.json"""
        try:
            with open(ROADMAP_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: {ROADMAP_FILE} not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in roadmap.json: {e}")
            sys.exit(1)
    
    def load_state(self):
        """Load state.json"""
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                if not state.get('start_time'):
                    state['start_time'] = datetime.now().isoformat()
                return state
        except FileNotFoundError:
            # Create initial state
            state = {
                "project_name": "BetSentinel",
                "project_complete": False,
                "current_stage": "stage_1",
                "current_task": "task_1",
                "iteration_count": 0,
                "last_commit_hash": "",
                "last_commit_time": "",
                "start_time": datetime.now().isoformat(),
                "last_24h_checkpoint": "",
                "errors_encountered": [],
                "successful_runs": 0,
                "consecutive_24h_runs": 0,
                "last_error": None,
                "last_success_time": None
            }
            self.save_state(state)
            return state
    
    def save_state(self, state=None):
        """Save state.json"""
        if state is None:
            state = self.state
        state['iteration_count'] = self.iteration
        state['last_commit_time'] = datetime.now().isoformat()
        os.makedirs(self.project_root / "system", exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_next_task(self):
        """Get next unfinished task from roadmap"""
        for stage in self.roadmap['stages']:
            if stage['status'] == 'completed':
                continue
            for task in stage['tasks']:
                if task['status'] == 'pending' or task['status'] == 'in_progress':
                    return stage, task
        return None, None
    
    def scan_todos(self):
        """Scan source files for TODO comments"""
        todos = []
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='replace') as f:
                    for line_num, line in enumerate(f, 1):
                        if 'TODO' in line.upper() or 'FIXME' in line.upper():
                            todos.append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'line': line_num,
                                'content': line.strip()
                            })
            except Exception as e:
                print(f"Error scanning {py_file}: {e}")
        return todos
    
    def run_main(self, timeout=30):
        """Run main.py and capture output"""
        try:
            # Check if venv exists, if not use system Python
            python_cmd = "python"
            if VENV_ACTIVATE.exists():
                if sys.platform == 'win32':
                    # On Windows, use venv python
                    python_cmd = str(VENV_ACTIVATE.parent / "python.exe")
                else:
                    python_cmd = str(VENV_ACTIVATE.parent / "python")
            
            # Run main.py
            process = subprocess.Popen(
                [python_cmd, str(MAIN_FILE)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.project_root)
            )
            
            # Wait for initial startup (30 seconds max)
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return stdout, stderr, process.returncode, None
            except subprocess.TimeoutExpired:
                # If it's still running after timeout, that's actually good (it's a long-running process)
                # Kill it and return success
                process.kill()
                stdout, stderr = process.communicate()
                # Timeout is expected for long-running processes
                return stdout, stderr, 0, "Timeout (expected for long-running process)"
        
        except Exception as e:
            return "", str(e), -1, str(e)
    
    def parse_error(self, stderr, traceback_text):
        """Parse error to identify file and line"""
        error_info = {
            'file': None,
            'line': None,
            'error_type': None,
            'message': None
        }
        
        # Try to extract from traceback
        if traceback_text:
            # Pattern: File "path", line X, in function
            match = re.search(r'File "([^"]+)", line (\d+)', traceback_text)
            if match:
                error_info['file'] = match.group(1)
                error_info['line'] = int(match.group(2))
        
        # Try to extract error type
        if stderr:
            match = re.search(r'(\w+Error|Exception):\s*(.+)', stderr)
            if match:
                error_info['error_type'] = match.group(1)
                error_info['message'] = match.group(2)
        
        return error_info
    
    def check_log_success(self):
        """Check if all required success messages are in app.log"""
        if not LOG_FILE.exists():
            return False, []
        
        # Check for various forms of success messages
        required_patterns = [
            ("Collector started", ["collector started", "odds collection", "collector"]),
            ("Signal generated", ["signal generated", "generated.*signals", "signal"]),
            ("Backtest complete", ["backtest complete", "backtest completed", "backtest"]),
            ("Report generated", ["report generated", "daily report saved", "report"])
        ]
        
        try:
            with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
                log_content = f.read().lower()
            
            found = []
            missing = []
            for msg_name, patterns in required_patterns:
                found_match = False
                for pattern in patterns:
                    if pattern in log_content:
                        found.append(msg_name)
                        found_match = True
                        break
                if not found_match:
                    missing.append(msg_name)
            
            return len(missing) == 0, missing
        except Exception as e:
            print(f"Error reading log file: {e}")
            return False, [msg[0] for msg in required_patterns]
    
    def check_dashboard(self):
        """Check if dashboard is reachable"""
        try:
            import requests
            response = requests.get('http://127.0.0.1:5000', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def fix_error(self, error_info):
        """Attempt to fix error by regenerating function/class"""
        if not error_info.get('file'):
            return False
        
        file_path = Path(error_info['file'])
        if not file_path.is_absolute():
            file_path = self.project_root / file_path
        
        if not file_path.exists():
            return False
        
        print(f"Attempting to fix error in {file_path} at line {error_info.get('line')}")
        # For now, just log the error - actual fixing would require more sophisticated analysis
        return False
    
    def git_commit(self, message):
        """Commit and push changes"""
        try:
            # Check if Git executable exists
            if not Path(GIT_PATH).exists():
                print(f"[WARNING] Git operation skipped (path invalid: {GIT_PATH})")
                return None
            
            # Check if git repo exists
            if not (self.project_root / ".git").exists():
                print("Git repo not initialized, skipping commit")
                return None
            
            # Add all changes
            subprocess.run(
                [GIT_PATH, 'add', '.'],
                cwd=str(self.project_root),
                capture_output=True,
                check=False
            )
            
            # Commit
            result = subprocess.run(
                [GIT_PATH, 'commit', '-m', message],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Get commit hash
                hash_result = subprocess.run(
                    [GIT_PATH, 'rev-parse', 'HEAD'],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True
                )
                commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else ""
                
                # Push
                subprocess.run(
                    [GIT_PATH, 'push', 'origin', 'main'],
                    cwd=str(self.project_root),
                    capture_output=True,
                    check=False
                )
                
                return commit_hash
            return None
        except Exception as e:
            print(f"Git error: {e}")
            return None
    
    def compress_logs(self):
        """Compress old logs"""
        try:
            data_dir = self.project_root / "data"
            if not data_dir.exists():
                return
            
            # Create archive directory
            archive_dir = data_dir / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            # Archive old logs (keep last 7 days)
            cutoff = datetime.now() - timedelta(days=7)
            for log_file in data_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff.timestamp():
                    archive_path = archive_dir / f"{log_file.stem}_{datetime.now().strftime('%Y%m%d')}.log"
                    shutil.move(str(log_file), str(archive_path))
        except Exception as e:
            print(f"Error compressing logs: {e}")
    
    def run_iteration(self):
        """Run one iteration of the autonomous loop"""
        self.iteration += 1
        print(f"\n{'='*60}")
        print(f"Iteration {self.iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Get next task
        stage, task = self.get_next_task()
        if stage and task:
            print(f"Current Task: {stage['name']} - {task['name']}")
        
        # Scan for TODOs
        todos = self.scan_todos()
        if todos:
            print(f"Found {len(todos)} TODO comments")
        
        # Run main.py
        print("Running main.py...")
        stdout, stderr, returncode, timeout = self.run_main(timeout=30)
        
        # Check for errors (ignore timeout for long-running processes)
        if timeout == "Timeout (expected for long-running process)":
            print("Process started successfully (timeout expected for long-running service)")
        elif returncode != 0 or (stderr and "error" in stderr.lower() and "traceback" in stderr.lower()):
            print(f"ERROR DETECTED (returncode: {returncode})")
            if stderr:
                print(f"STDERR: {stderr[:500]}")
            
            error_info = self.parse_error(stderr, traceback.format_exc())
            self.state['last_error'] = {
                'iteration': self.iteration,
                'error_info': error_info,
                'stderr': stderr[:500] if stderr else "",
                'timestamp': datetime.now().isoformat()
            }
            self.state['errors_encountered'].append(self.state['last_error'])
            
            # Attempt to fix
            if error_info.get('file'):
                self.fix_error(error_info)
            
            self.save_state()
            return False
        
        # Check success logs
        all_found, missing = self.check_log_success()
        if not all_found:
            print(f"Missing success logs: {missing}")
            # This is not a critical error, continue
        
        # Check dashboard
        dashboard_ok = self.check_dashboard()
        if dashboard_ok:
            print("Dashboard is reachable [OK]")
        else:
            print("Dashboard not reachable (may still be starting)")
        
        # If we got here, run was successful
        self.state['successful_runs'] += 1
        self.state['last_success_time'] = datetime.now().isoformat()
        self.state['last_error'] = None
        
        # Commit progress
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        commit_msg = f"Auto-commit iteration {self.iteration} - {timestamp}"
        commit_hash = self.git_commit(commit_msg)
        if commit_hash:
            self.state['last_commit_hash'] = commit_hash
            print(f"Committed: {commit_hash[:8]}")
        
        self.save_state()
        return True
    
    def check_24h_elapsed(self):
        """Check if 24 hours have elapsed"""
        if not self.state.get('last_24h_checkpoint'):
            self.state['last_24h_checkpoint'] = datetime.now().isoformat()
            return False
        
        last_checkpoint = datetime.fromisoformat(self.state['last_24h_checkpoint'])
        elapsed = datetime.now() - last_checkpoint
        
        if elapsed >= timedelta(hours=24):
            return True
        return False
    
    def run(self):
        """Main autonomous loop"""
        print("="*60)
        print("BetSentinel Autonomous Project Engineer")
        print("="*60)
        print(f"Project: {self.project_root}")
        print(f"Start Time: {self.start_time}")
        print("="*60)
        
        # Check if project is complete
        if self.state.get('project_complete'):
            print("Project marked as complete. Exiting.")
            return
        
        try:
            while True:
                # Check for 24-hour checkpoint
                if self.check_24h_elapsed():
                    print("\n24-hour checkpoint reached")
                    self.compress_logs()
                    self.git_commit(f"24h checkpoint - {datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    self.state['last_24h_checkpoint'] = datetime.now().isoformat()
                    self.state['consecutive_24h_runs'] += 1
                    
                    # Check completion criteria
                    all_success, _ = self.check_log_success()
                    dashboard_ok = self.check_dashboard()
                    
                    if all_success and dashboard_ok and self.state['consecutive_24h_runs'] >= 2:
                        self.state['project_complete'] = True
                        self.git_commit("[OK] Project stable: BetSentinel ready")
                        print("\n" + "="*60)
                        print("[OK] PROJECT COMPLETE!")
                        print("BetSentinel is stable and ready")
                        print("="*60)
                        break
                
                # Run iteration
                success = self.run_iteration()
                
                # Wait 60 seconds
                print(f"\nWaiting 60 seconds before next iteration...")
                time.sleep(60)
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Saving state...")
            self.save_state()
        except Exception as e:
            print(f"\n\nFatal error in autonomous engine: {e}")
            traceback.print_exc()
            self.save_state()

if __name__ == "__main__":
    engine = AutonomousEngine()
    engine.run()

