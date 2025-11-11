"""
Flask Dashboard - Web interface for BetSentinel
"""
from flask import Flask, render_template_string, jsonify
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime, timedelta

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    
    # Dashboard HTML template
    DASHBOARD_HTML = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BetSentinel Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .header h1 {
                color: #333;
                margin-bottom: 10px;
            }
            .header p {
                color: #666;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-card h3 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 14px;
                text-transform: uppercase;
            }
            .stat-card .value {
                font-size: 32px;
                font-weight: bold;
                color: #333;
            }
            .content {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .content h2 {
                color: #333;
                margin-bottom: 20px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #667eea;
                color: white;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .status {
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            .status.active {
                background: #4caf50;
                color: white;
            }
            .status.inactive {
                background: #f44336;
                color: white;
            }
            .refresh-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 20px;
            }
            .refresh-btn:hover {
                background: #5568d3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚽ BetSentinel Dashboard</h1>
                <p>Football Exchange Agent - Real-time Monitoring</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>Total Events</h3>
                    <div class="value" id="total-events">-</div>
                </div>
                <div class="stat-card">
                    <h3>Recent Signals</h3>
                    <div class="value" id="recent-signals">-</div>
                </div>
                <div class="stat-card">
                    <h3>Avg Odds</h3>
                    <div class="value" id="avg-odds">-</div>
                </div>
                <div class="stat-card">
                    <h3>Status</h3>
                    <div class="value">
                        <span class="status active">ACTIVE</span>
                    </div>
                </div>
            </div>
            
            <div class="content">
                <h2>Recent Odds Data</h2>
                <div id="odds-table">
                    <p>Loading...</p>
                </div>
                <button class="refresh-btn" onclick="loadData()">Refresh Data</button>
            </div>
        </div>
        
        <script>
            function loadData() {
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('total-events').textContent = data.total_events || 0;
                        document.getElementById('recent-signals').textContent = data.recent_signals || 0;
                        document.getElementById('avg-odds').textContent = data.avg_odds ? data.avg_odds.toFixed(2) : '-';
                    });
                
                fetch('/api/recent-odds')
                    .then(response => response.json())
                    .then(data => {
                        const table = document.getElementById('odds-table');
                        if (data.length === 0) {
                            table.innerHTML = '<p>No recent odds data available.</p>';
                            return;
                        }
                        
                        let html = '<table><thead><tr><th>Time</th><th>Home Team</th><th>Away Team</th><th>Bookmaker</th><th>Outcome</th><th>Odds</th></tr></thead><tbody>';
                        data.forEach(row => {
                            html += `<tr>
                                <td>${row.timestamp}</td>
                                <td>${row.home_team || '-'}</td>
                                <td>${row.away_team || '-'}</td>
                                <td>${row.bookmaker || '-'}</td>
                                <td>${row.outcome_name || '-'}</td>
                                <td>${row.price ? row.price.toFixed(2) : '-'}</td>
                            </tr>`;
                        });
                        html += '</tbody></table>';
                        table.innerHTML = html;
                    });
            }
            
            // Load data on page load
            loadData();
            
            // Auto-refresh every 30 seconds
            setInterval(loadData, 30000);
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def dashboard():
        """Main dashboard page"""
        return render_template_string(DASHBOARD_HTML)
    
    @app.route('/api/stats')
    def api_stats():
        """API endpoint for statistics"""
        try:
            conn = sqlite3.connect('data/odds.db')
            
            # Total events
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(DISTINCT home_team || away_team || commence_time) FROM odds')
            total_events = cursor.fetchone()[0] or 0
            
            # Recent signals count (last hour)
            signals_file = 'data/signals.log'
            recent_signals = 0
            if os.path.exists(signals_file):
                cutoff = datetime.now() - timedelta(hours=1)
                with open(signals_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                parts = line.split(' | ')
                                if len(parts) >= 1:
                                    signal_time = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S.%f')
                                    if signal_time >= cutoff:
                                        recent_signals += 1
                            except:
                                continue
            
            # Average odds
            df = pd.read_sql_query('SELECT AVG(price) as avg_price FROM odds', conn)
            avg_odds = float(df['avg_price'].iloc[0]) if not df.empty and not pd.isna(df['avg_price'].iloc[0]) else None
            
            conn.close()
            
            return jsonify({
                'total_events': total_events,
                'recent_signals': recent_signals,
                'avg_odds': avg_odds
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/recent-odds')
    def api_recent_odds():
        """API endpoint for recent odds"""
        try:
            conn = sqlite3.connect('data/odds.db')
            cutoff = datetime.now() - timedelta(hours=1)
            
            query = '''
                SELECT timestamp, home_team, away_team, bookmaker, outcome_name, price
                FROM odds 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 50
            '''
            
            df = pd.read_sql_query(query, conn, params=(cutoff,))
            conn.close()
            
            # Convert to list of dicts
            data = df.to_dict('records')
            
            # Format timestamp
            for row in data:
                if 'timestamp' in row and row['timestamp']:
                    try:
                        dt = pd.to_datetime(row['timestamp'])
                        row['timestamp'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
            
            return jsonify(data)
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)

