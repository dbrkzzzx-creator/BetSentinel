from flask import Blueprint, jsonify, request
from app.utils.automation_manager import automation_manager

automation_bp = Blueprint("automation", __name__, url_prefix="/api/automation")

@automation_bp.route("/rules", methods=["GET"])
def get_rules():
    """Get automation rules"""
    return jsonify(automation_manager.rules)

@automation_bp.route("/rules", methods=["POST"])
def save_rules():
    """Save automation rules"""
    try:
        rules = request.get_json()
        if automation_manager.save_rules(rules):
            automation_manager.add_log("rules_updated", "Automation rules updated", rules)
            return jsonify({"status": "ok", "rules": rules})
        else:
            return jsonify({"status": "error", "message": "Failed to save rules"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@automation_bp.route("/start", methods=["POST"])
def start_automation():
    """Start automation"""
    if automation_manager.running:
        return jsonify({"status": "error", "message": "Automation already running"}), 400
    
    if automation_manager.start():
        return jsonify({"status": "ok", "message": "Automation started"})
    else:
        return jsonify({"status": "error", "message": "Failed to start automation"}), 500

@automation_bp.route("/stop", methods=["POST"])
def stop_automation():
    """Stop automation"""
    if not automation_manager.running:
        return jsonify({"status": "error", "message": "Automation not running"}), 400
    
    if automation_manager.stop():
        return jsonify({"status": "ok", "message": "Automation stopped"})
    else:
        return jsonify({"status": "error", "message": "Failed to stop automation"}), 500

@automation_bp.route("/status", methods=["GET"])
def get_status():
    """Get automation status"""
    return jsonify(automation_manager.get_status())

@automation_bp.route("/logs", methods=["GET"])
def get_logs():
    """Get automation logs"""
    limit = request.args.get("limit", 50, type=int)
    return jsonify({
        "logs": automation_manager.get_recent_logs(limit),
        "total": len(automation_manager.logs)
    })

