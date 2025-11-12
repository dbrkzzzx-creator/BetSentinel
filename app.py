from flask import Flask
from flask_cors import CORS
from app.routes import events, rules, status

app = Flask(__name__)
CORS(app)

app.register_blueprint(events.bp)
app.register_blueprint(rules.bp)
app.register_blueprint(status.bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

