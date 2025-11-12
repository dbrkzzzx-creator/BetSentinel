from flask import Blueprint, jsonify
from app.utils.cache import cache

bp = Blueprint("events", __name__, url_prefix="/api")

@bp.route("/events", methods=["GET"])
def get_events():
    data = cache.get("mock_events")
    if not data:
        data = [
            {"match": "Liverpool vs Arsenal", "odds": {"home": 1.8, "draw": 3.4, "away": 4.2}},
            {"match": "Chelsea vs Man City", "odds": {"home": 3.2, "draw": 3.1, "away": 2.1}},
        ]
        cache["mock_events"] = data
    return jsonify(data)

