"""
Automation Manager - Handles bet automation logic and state
"""
import json
import threading
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

AUTOMATION_RULES_FILE = Path("data/automation_rules.json")
AUTOMATION_LOG_FILE = Path("data/automation_log.json")

class AutomationManager:
    """Manages bet automation state and execution"""
    
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.total_spent = 0.0
        self.lock = threading.Lock()
        self.rules = self.load_rules()
        self.logs: List[Dict] = []
        self.load_logs()
    
    def load_rules(self) -> Dict:
        """Load automation rules from file"""
        if AUTOMATION_RULES_FILE.exists():
            try:
                with open(AUTOMATION_RULES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading rules: {e}")
        return {
            "min_bet": 10.0,
            "max_bet": 100.0,
            "daily_cap": 1000.0,
            "whitelist": [],
            "blacklist": [],
            "enabled": False
        }
    
    def save_rules(self, rules: Dict) -> bool:
        """Save automation rules to file"""
        try:
            AUTOMATION_RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(AUTOMATION_RULES_FILE, 'w', encoding='utf-8') as f:
                json.dump(rules, f, indent=2)
            self.rules = rules
            return True
        except Exception as e:
            logger.error(f"Error saving rules: {e}")
            return False
    
    def load_logs(self):
        """Load automation logs from file"""
        if AUTOMATION_LOG_FILE.exists():
            try:
                with open(AUTOMATION_LOG_FILE, 'r', encoding='utf-8') as f:
                    self.logs = json.load(f)
            except Exception as e:
                logger.error(f"Error loading logs: {e}")
                self.logs = []
        else:
            self.logs = []
    
    def save_logs(self):
        """Save automation logs to file"""
        try:
            AUTOMATION_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(AUTOMATION_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.logs[-1000:], f, indent=2)  # Keep last 1000 entries
        except Exception as e:
            logger.error(f"Error saving logs: {e}")
    
    def add_log(self, event_type: str, message: str, data: Optional[Dict] = None):
        """Add a log entry"""
        with self.lock:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": event_type,
                "message": message,
                "data": data or {}
            }
            self.logs.append(log_entry)
            self.save_logs()
            logger.info(f"[AUTOMATION] {event_type}: {message}")
    
    def evaluate_event(self, match: str, odds: Dict) -> Optional[Dict]:
        """Evaluate if a bet should be placed on this event"""
        if not self.rules.get("enabled", False):
            return None
        
        # Check whitelist/blacklist
        if self.rules.get("whitelist") and match not in self.rules["whitelist"]:
            return None
        
        if match in self.rules.get("blacklist", []):
            return None
        
        # Simple evaluation: bet on highest odds outcome
        max_odds_key = max(odds.keys(), key=lambda k: odds[k])
        max_odds = odds[max_odds_key]
        
        # Only bet if odds are reasonable (between 1.5 and 5.0)
        if 1.5 <= max_odds <= 5.0:
            bet_amount = min(
                self.rules.get("max_bet", 100.0),
                max(self.rules.get("min_bet", 10.0), max_odds * 10)
            )
            
            return {
                "match": match,
                "outcome": max_odds_key,
                "odds": max_odds,
                "amount": bet_amount
            }
        
        return None
    
    def place_bet(self, bet: Dict) -> bool:
        """Simulate placing a bet"""
        with self.lock:
            # Check daily cap
            if self.total_spent + bet["amount"] > self.rules.get("daily_cap", 1000.0):
                self.add_log("bet_rejected", f"Daily cap reached. Total spent: {self.total_spent}", bet)
                return False
            
            # Place bet (simulated)
            self.total_spent += bet["amount"]
            self.add_log("bet_placed", f"Placed bet on {bet['match']}", bet)
            return True
    
    def start(self):
        """Start automation thread"""
        if self.running:
            return False
        
        with self.lock:
            self.running = True
            self.total_spent = 0.0
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            self.add_log("automation_started", "Bet automation started")
            return True
    
    def stop(self):
        """Stop automation thread"""
        if not self.running:
            return False
        
        with self.lock:
            self.running = False
            self.add_log("automation_stopped", f"Bet automation stopped. Total spent: {self.total_spent}")
            return True
    
    def _run_loop(self):
        """Main automation loop"""
        while self.running:
            try:
                # Simulate checking for events every 30 seconds
                time.sleep(30)
                
                if not self.running:
                    break
                
                # Mock event data (in real implementation, fetch from API)
                mock_events = [
                    {"match": "Liverpool vs Arsenal", "odds": {"home": 1.8, "draw": 3.4, "away": 4.2}},
                    {"match": "Chelsea vs Man City", "odds": {"home": 3.2, "draw": 3.1, "away": 2.1}},
                ]
                
                for event in mock_events:
                    if not self.running:
                        break
                    
                    bet_decision = self.evaluate_event(event["match"], event["odds"])
                    if bet_decision:
                        self.place_bet(bet_decision)
                    
                    # Check daily cap
                    if self.total_spent >= self.rules.get("daily_cap", 1000.0):
                        self.add_log("cap_reached", f"Daily cap reached: {self.total_spent}")
                        self.stop()
                        break
                
            except Exception as e:
                logger.error(f"Error in automation loop: {e}")
                self.add_log("error", f"Automation error: {str(e)}")
                time.sleep(10)
    
    def get_status(self) -> Dict:
        """Get current automation status"""
        with self.lock:
            return {
                "running": self.running,
                "total_spent": self.total_spent,
                "daily_cap": self.rules.get("daily_cap", 1000.0),
                "remaining": max(0, self.rules.get("daily_cap", 1000.0) - self.total_spent),
                "rules": self.rules,
                "log_count": len(self.logs)
            }
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent log entries"""
        with self.lock:
            return self.logs[-limit:]

# Global instance
automation_manager = AutomationManager()

