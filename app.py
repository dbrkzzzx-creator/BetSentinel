from flask import Flask
from flask_cors import CORS
from app.routes import events, rules, status
from app.routes.automation import automation_bp
from pathlib import Path
import json
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

# Auto-create status.json if missing
STATUS_FILE = Path("data/status.json")
if not STATUS_FILE.exists():
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "status": "running",
            "last_update": datetime.now(timezone.utc).isoformat(),
            "iterations": 0,
            "errors": 0
        }, f, indent=2)

app.register_blueprint(events.bp)
app.register_blueprint(rules.bp)
app.register_blueprint(status.bp)
app.register_blueprint(automation_bp)

if __name__ == "__main__":
    print("=" * 60)
    print("Running Flask backend on port 5000")
    print("CORS enabled for http://localhost:3000 and http://localhost:5173")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)

