"""
Continuous Monitor for BetSentinel Autonomous Engine
Monitors system stability and auto-commits successful iterations
"""
import os
import sys
import io
import time
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Fix UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent
LOG_FILE = PROJECT_ROOT / "data" / "app.log"
ENGINE_LOG = PROJECT_ROOT / "data" / "engine_run.log"
STATE_FILE = PROJECT_ROOT / "system" / "state.json"
CHECK_INTERVAL = 60  # Check every 60 seconds
GIT_PATH = r"D:\AI\Git\bin\git.exe"

class StabilityMonitor:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.start_time = datetime.now()
        self.last_commit_time = None
        self.successful_checks = 0
        self.consecutive_success_hours = 0
        self.last_24h_checkpoint = datetime.now()
        self.errors_detected = []
        
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
    def check_dashboard(self):
        """Check if dashboard is reachable"""
        try:
            response = requests.get('http://127.0.0.1:5000', timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.log(f"Dashboard check failed: {e}", "WARNING")
            return False
    
    def check_success_logs(self):
        """Check if all required success messages are in app.log"""
        if not LOG_FILE.exists():
            return False, []
        
        required_messages = [
            "Collector started",
            "Signal generated",
            "Backtest complete",
            "Report generated"
        ]
        
        try:
            with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
                log_content = f.read().lower()
            
            found = []
            missing = []
            for msg in required_messages:
                if msg.lower() in log_content:
                    found.append(msg)
                else:
                    missing.append(msg)
            
            return len(missing) == 0, missing
        except Exception as e:
            self.log(f"Error reading log file: {e}", "ERROR")
            return False, required_messages
    
    def check_errors(self):
        """Check for errors in engine_run.log"""
        if not ENGINE_LOG.exists():
            return False, []
        
        error_patterns = [
            "UnicodeEncodeError",
            "utf-8 codec",
            "charmap codec",
            "ERROR",
            "Traceback",
            "Exception"
        ]
        
        try:
            with open(ENGINE_LOG, 'r', encoding='utf-8', errors='replace') as f:
                # Read last 100 lines
                lines = f.readlines()
                recent_lines = lines[-100:] if len(lines) > 100 else lines
                log_content = '\n'.join(recent_lines).lower()
            
            errors = []
            for pattern in error_patterns:
                if pattern.lower() in log_content:
                    # Check if it's a real error (not just INFO level)
                    for line in recent_lines:
                        if pattern.lower() in line.lower() and 'error' in line.lower():
                            errors.append(line.strip())
                            break
            
            return len(errors) == 0, errors
        except Exception as e:
            self.log(f"Error reading engine log: {e}", "ERROR")
            return False, []
    
    def git_commit(self, message):
        """Commit and push changes"""
        try:
            if not Path(GIT_PATH).exists():
                self.log(f"Git not found at {GIT_PATH}, skipping commit", "WARNING")
                return False
            
            # Add all changes
            result = subprocess.run(
                [GIT_PATH, 'add', '.'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.log(f"Git add failed: {result.stderr}", "WARNING")
                return False
            
            # Commit
            result = subprocess.run(
                [GIT_PATH, 'commit', '-m', message],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Push
                push_result = subprocess.run(
                    [GIT_PATH, 'push', 'origin', 'main'],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True
                )
                
                if push_result.returncode == 0:
                    self.log("Successfully committed and pushed", "SUCCESS")
                    self.last_commit_time = datetime.now()
                    return True
                else:
                    self.log(f"Git push failed: {push_result.stderr}", "WARNING")
                    return False
            else:
                if "nothing to commit" in result.stdout.lower():
                    self.log("No changes to commit", "INFO")
                    return True
                else:
                    self.log(f"Git commit failed: {result.stderr}", "WARNING")
                    return False
        
        except Exception as e:
            self.log(f"Error in git commit: {e}", "ERROR")
            return False
    
    def update_state(self, all_logs_found, dashboard_ok, no_errors):
        """Update state.json with current status"""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r', encoding='utf-8', errors='replace') as f:
                    state = json.load(f)
            else:
                state = {
                    "project_complete": False,
                    "iteration_count": 0,
                    "current_stage": "stage_1"
                }
            
            # Update status
            state['last_check_time'] = datetime.now().isoformat()
            state['all_logs_found'] = all_logs_found
            state['dashboard_ok'] = dashboard_ok
            state['no_errors'] = no_errors
            state['successful_checks'] = self.successful_checks
            state['consecutive_success_hours'] = self.consecutive_success_hours
            
            # Check if stable for 24 hours
            elapsed = datetime.now() - self.last_24h_checkpoint
            if elapsed >= timedelta(hours=24):
                if all_logs_found and dashboard_ok and no_errors:
                    self.consecutive_success_hours += 1
                    if self.consecutive_success_hours >= 2:
                        state['project_complete'] = True
                        self.log("=" * 60, "SUCCESS")
                        self.log("[OK] Project stable for 24+ hours - MARKING COMPLETE", "SUCCESS")
                        self.log("=" * 60, "SUCCESS")
                else:
                    self.consecutive_success_hours = 0
                self.last_24h_checkpoint = datetime.now()
            
            # Save state
            os.makedirs(self.project_root / "system", exist_ok=True)
            with open(STATE_FILE, 'w', encoding='utf-8', errors='replace') as f:
                json.dump(state, f, indent=2)
            
            return state.get('project_complete', False)
        except Exception as e:
            self.log(f"Error updating state: {e}", "ERROR")
            return False
    
    def run_check(self):
        """Run a single stability check"""
        self.log("=" * 60)
        self.log("Running stability check...")
        
        # Check dashboard
        dashboard_ok = self.check_dashboard()
        self.log(f"Dashboard reachable: {dashboard_ok}")
        
        # Check success logs
        all_logs_found, missing = self.check_success_logs()
        if all_logs_found:
            self.log("All success logs found: [OK]")
        else:
            self.log(f"Missing success logs: {missing}")
        
        # Check for errors
        no_errors, errors = self.check_errors()
        if no_errors:
            self.log("No errors detected: [OK]")
        else:
            self.log(f"Errors detected: {len(errors)} errors found")
            self.errors_detected.extend(errors)
        
        # Determine if check was successful
        check_success = all_logs_found and dashboard_ok and no_errors
        
        if check_success:
            self.successful_checks += 1
            self.log(f"Check successful! Total successful checks: {self.successful_checks}")
            
            # Auto-commit on success
            if self.last_commit_time is None or (datetime.now() - self.last_commit_time) >= timedelta(minutes=5):
                self.git_commit("Auto: verified stable iteration")
        else:
            self.log("Check failed - issues detected", "WARNING")
        
        # Update state
        project_complete = self.update_state(all_logs_found, dashboard_ok, no_errors)
        
        # Calculate uptime
        uptime = datetime.now() - self.start_time
        self.log(f"Uptime: {uptime}")
        self.log(f"Consecutive success hours: {self.consecutive_success_hours}")
        self.log("=" * 60)
        
        return check_success, project_complete
    
    def run(self):
        """Main monitoring loop"""
        self.log("=" * 60)
        self.log("BetSentinel Stability Monitor Started")
        self.log("=" * 60)
        self.log(f"Project: {self.project_root}")
        self.log(f"Start Time: {self.start_time}")
        self.log(f"Check Interval: {CHECK_INTERVAL} seconds")
        self.log("=" * 60)
        
        try:
            while True:
                check_success, project_complete = self.run_check()
                
                if project_complete:
                    self.log("=" * 60)
                    self.log("[OK] PROJECT COMPLETE - Stable for 24+ hours!")
                    self.log("=" * 60)
                    break
                
                # Wait for next check
                self.log(f"\nWaiting {CHECK_INTERVAL} seconds until next check...")
                time.sleep(CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            self.log("\nMonitor interrupted by user", "INFO")
        except Exception as e:
            self.log(f"Fatal error in monitor: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")

if __name__ == "__main__":
    monitor = StabilityMonitor()
    monitor.run()

