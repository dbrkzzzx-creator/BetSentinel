"""
Supervisor for BetSentinel Autonomous Engineering System
Monitors and manages the autonomous engine with full observability
"""
import os
import sys
import subprocess
import time
import json
import traceback
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
VENV_ACTIVATE = PROJECT_ROOT / "venv" / "Scripts" / "activate"
ENGINE_FILE = PROJECT_ROOT / "autonomous_engine.py"
LOG_FILE = PROJECT_ROOT / "data" / "engine_run.log"
ROADMAP_FILE = PROJECT_ROOT / "roadmap.json"
STATE_FILE = PROJECT_ROOT / "system" / "state.json"

class Supervisor:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.iteration_count = 0
        self.last_status = "unknown"
        self.start_time = datetime.now()
        self.last_checkpoint = None
        self.restart_count = 0
        self.max_restarts = 1
        
        # Ensure data directory exists
        os.makedirs(self.project_root / "data", exist_ok=True)
        os.makedirs(self.project_root / "system", exist_ok=True)
        
    def log(self, message, level="INFO"):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def load_roadmap(self):
        """Load roadmap.json"""
        try:
            with open(ROADMAP_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Error loading roadmap: {e}", "ERROR")
            return None
    
    def load_state(self):
        """Load state.json"""
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "project_complete": False,
                "iteration_count": 0,
                "current_stage": "stage_1"
            }
        except Exception as e:
            self.log(f"Error loading state: {e}", "ERROR")
            return None
    
    def get_current_stage_info(self):
        """Get current stage information from roadmap"""
        roadmap = self.load_roadmap()
        state = self.load_state()
        
        if not roadmap or not state:
            return "Unknown", "Unknown"
        
        current_stage_id = state.get('current_stage', 'stage_1')
        
        for stage in roadmap.get('stages', []):
            if stage.get('id') == current_stage_id:
                return stage.get('name', 'Unknown'), stage.get('status', 'unknown')
        
        return "Unknown", "Unknown"
    
    def check_log_success(self):
        """Check if required success messages are in app.log"""
        app_log = self.project_root / "data" / "app.log"
        if not app_log.exists():
            return False, []
        
        required_messages = [
            "Collector started",
            "Signal generated",
            "Backtest complete",
            "Report generated"
        ]
        
        try:
            with open(app_log, 'r', encoding='utf-8') as f:
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
            self.log(f"Error checking log success: {e}", "ERROR")
            return False, required_messages
    
    def git_commit_success(self):
        """Commit and push on successful iteration"""
        try:
            # Check if git repo exists
            if not (self.project_root / ".git").exists():
                self.log("Git repo not initialized, skipping commit", "WARNING")
                return False
            
            # Add all changes
            result = subprocess.run(
                ['git', 'add', '.'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.log(f"Git add failed: {result.stderr}", "WARNING")
                return False
            
            # Commit
            commit_msg = "auto iteration - success"
            result = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Push
                push_result = subprocess.run(
                    ['git', 'push', 'origin', 'main'],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True
                )
                
                if push_result.returncode == 0:
                    self.log("Successfully committed and pushed", "SUCCESS")
                    return True
                else:
                    self.log(f"Git push failed: {push_result.stderr}", "WARNING")
                    return False
            else:
                # No changes to commit is okay
                if "nothing to commit" in result.stdout.lower():
                    self.log("No changes to commit", "INFO")
                    return True
                else:
                    self.log(f"Git commit failed: {result.stderr}", "WARNING")
                    return False
        
        except Exception as e:
            self.log(f"Error in git commit: {e}", "ERROR")
            return False
    
    def check_24h_checkpoint(self):
        """Check if 24 hours have elapsed since last checkpoint"""
        state = self.load_state()
        if not state:
            return False
        
        last_checkpoint_str = state.get('last_24h_checkpoint', '')
        if not last_checkpoint_str:
            return False
        
        try:
            last_checkpoint = datetime.fromisoformat(last_checkpoint_str)
            elapsed = datetime.now() - last_checkpoint
            return elapsed >= timedelta(hours=24)
        except:
            return False
    
    def run_engine(self):
        """Run the autonomous engine and capture output"""
        self.log("=" * 60)
        self.log("Starting Autonomous Engine")
        self.log("=" * 60)
        
        # Determine Python command
        python_cmd = "python"
        if VENV_ACTIVATE.exists():
            if sys.platform == 'win32':
                python_cmd = str(VENV_ACTIVATE.parent / "python.exe")
            else:
                python_cmd = str(VENV_ACTIVATE.parent / "python")
        
        process = None
        try:
            # Run engine as subprocess
            process = subprocess.Popen(
                [python_cmd, str(ENGINE_FILE)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=str(self.project_root)
            )
            
            # Stream output in real-time
            last_check_time = time.time()
            check_interval = 60  # Check for success every 60 seconds
            
            while True:
                # Check if process is still running
                if process.poll() is not None:
                    # Process ended
                    return_code = process.returncode
                    # Read any remaining output
                    remaining = process.stdout.read()
                    if remaining:
                        for line in remaining.splitlines():
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            log_line = f"[{timestamp}] {line}"
                            print(log_line)
                            try:
                                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                                    f.write(log_line + '\n')
                            except:
                                pass
                    return return_code
                
                # Read available output
                line = process.stdout.readline()
                if line:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_line = f"[{timestamp}] {line.rstrip()}"
                    print(log_line)
                    
                    try:
                        with open(LOG_FILE, 'a', encoding='utf-8') as f:
                            f.write(log_line + '\n')
                    except:
                        pass
                
                # Periodically check for success and commit
                current_time = time.time()
                if current_time - last_check_time >= check_interval:
                    all_found, missing = self.check_log_success()
                    if all_found:
                        self.log("Success logs detected - committing...", "INFO")
                        self.git_commit_success()
                    last_check_time = current_time
                
                # Small sleep to avoid busy waiting
                time.sleep(0.1)
            
        except KeyboardInterrupt:
            self.log("Interrupted by user", "INFO")
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except:
                    process.kill()
            return -1
        except Exception as e:
            self.log(f"Error running engine: {e}", "ERROR")
            self.log(traceback.format_exc(), "ERROR")
            if process:
                process.terminate()
            return -1
    
    def summarize_iteration(self):
        """Summarize current status"""
        state = self.load_state()
        roadmap = self.load_roadmap()
        
        if not state:
            return
        
        stage_name, stage_status = self.get_current_stage_info()
        iteration_count = state.get('iteration_count', 0)
        
        self.log("=" * 60)
        self.log("ITERATION SUMMARY")
        self.log("=" * 60)
        self.log(f"Current Roadmap Stage: {stage_name} ({stage_status})")
        self.log(f"Total Iterations: {iteration_count}")
        self.log(f"Last Run Status: {self.last_status}")
        self.log(f"Restart Count: {self.restart_count}")
        self.log("=" * 60)
    
    def check_completion(self):
        """Check if project is complete"""
        state = self.load_state()
        if not state:
            return False
        
        # Check state.json
        if state.get('project_complete', False):
            return True
        
        # Check roadmap
        roadmap = self.load_roadmap()
        if roadmap:
            stage_3 = None
            for stage in roadmap.get('stages', []):
                if stage.get('id') == 'stage_3':
                    stage_3 = stage
                    break
            
            if stage_3 and stage_3.get('status') == 'completed':
                return True
        
        return False
    
    def run(self):
        """Main supervisor loop"""
        self.log("=" * 60)
        self.log("BetSentinel Autonomous Engineering Supervisor")
        self.log("=" * 60)
        self.log(f"Project: {self.project_root}")
        self.log(f"Start Time: {self.start_time}")
        self.log("=" * 60)
        
        try:
            while True:
                # Check for completion
                if self.check_completion():
                    self.log("=" * 60)
                    self.log("✅ Project stable: BetSentinel ready")
                    self.log("=" * 60)
                    break
                
                # Check for 24-hour checkpoint
                if self.check_24h_checkpoint():
                    self.log("Checkpoint reached — system stable for 24 hours.", "CHECKPOINT")
                    self.last_checkpoint = datetime.now()
                
                # Run engine (this will run until completion or crash)
                self.log(f"\nStarting engine (restart attempt {self.restart_count + 1})...")
                return_code = self.run_engine()
                
                # Check if engine completed (0 = success, -1 = interrupted, other = error)
                if return_code == 0:
                    self.last_status = "success"
                    self.log("Engine completed successfully", "SUCCESS")
                    
                    # Final check for success logs
                    all_found, missing = self.check_log_success()
                    if all_found:
                        self.log("All success logs found!", "SUCCESS")
                        self.git_commit_success()
                    else:
                        self.log(f"Missing success logs: {missing}", "WARNING")
                    
                    # Summarize
                    self.summarize_iteration()
                    
                    # Check if project is complete
                    if self.check_completion():
                        break
                    
                    # Reset restart count on success
                    self.restart_count = 0
                    
                elif return_code == -1:
                    # Interrupted - exit gracefully
                    self.log("Engine interrupted", "INFO")
                    break
                    
                else:
                    self.last_status = "failed"
                    self.restart_count += 1
                    
                    self.log(f"Engine exited with code {return_code}", "ERROR")
                    self.summarize_iteration()
                    
                    # Restart if under limit
                    if self.restart_count <= self.max_restarts:
                        self.log(f"Restarting engine in 30 seconds... (attempt {self.restart_count}/{self.max_restarts})", "WARNING")
                        time.sleep(30)
                    else:
                        self.log("Max restarts reached. Stopping supervisor.", "ERROR")
                        break
        
        except KeyboardInterrupt:
            self.log("\nSupervisor interrupted by user", "INFO")
        except Exception as e:
            self.log(f"Fatal error in supervisor: {e}", "ERROR")
            self.log(traceback.format_exc(), "ERROR")
        finally:
            self.log("Supervisor stopped", "INFO")

if __name__ == "__main__":
    supervisor = Supervisor()
    supervisor.run()

