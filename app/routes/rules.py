from flask import Blueprint, jsonify, request
from pathlib import Path
import json

bp = Blueprint("rules", __name__, url_prefix="/api")

DATA_FILE = Path("data/rules.json")

@bp.route("/rules", methods=["POST"])
def save_rules():
    rules = request.get_json()
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)
    return jsonify({"status": "ok", "rules": rules})

@bp.route("/rules", methods=["GET"])
def get_rules():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"status": "empty"})

