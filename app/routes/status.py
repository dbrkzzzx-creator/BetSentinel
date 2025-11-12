from flask import Blueprint, jsonify
import json
from pathlib import Path
from datetime import datetime, timezone

bp = Blueprint("status", __name__, url_prefix="/api")
STATUS_FILE = Path("data/status.json")

@bp.route("/status", methods=["GET"])
def get_status():
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    else:
        data = {"status": "unknown", "last_update": datetime.now(timezone.utc).isoformat()}
    return jsonify(data)

