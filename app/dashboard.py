"""
Flask Dashboard - Web interface for BetSentinel
"""
from flask import Flask, render_template_string, jsonify
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

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
            .nav-links {
                display: flex;
                gap: 20px;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }
            .nav-links a {
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
                padding: 5px 10px;
                border-radius: 5px;
                transition: background 0.3s;
            }
            .nav-links a:hover, .nav-links a.active {
                background: #667eea;
                color: white;
            }
            .status-bar {
                display: flex;
                gap: 20px;
                margin-top: 15px;
                padding: 15px;
                background: #f5f5f5;
                border-radius: 5px;
                align-items: center;
            }
            .status-bar-item {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .status-bar-item label {
                font-weight: 600;
                color: #666;
            }
            .status-badge {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
            .status-badge.running {
                background: #4caf50;
                color: white;
            }
            .status-badge.error {
                background: #f44336;
                color: white;
            }
            .status-badge.stuck {
                background: #ff9800;
                color: white;
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
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h1>⚽ BetSentinel Dashboard</h1>
                        <p>Football Exchange Agent - Real-time Monitoring</p>
                    </div>
                    <div style="font-size: 24px;">🔔</div>
                </div>
                <div class="nav-links">
                    <a href="#" class="active">Analytics</a>
                    <a href="#">Insights</a>
                    <a href="#">Signals</a>
                    <a href="#">Backtest</a>
                    <a href="#">Reports</a>
                </div>
                <div class="status-bar">
                    <div class="status-bar-item">
                        <label>Status:</label>
                        <span class="status-badge" id="status-badge">running</span>
                    </div>
                    <div class="status-bar-item">
                        <label>Matches:</label>
                        <span id="matches-count">-</span>
                    </div>
                    <div class="status-bar-item">
                        <label>Last Update:</label>
                        <span id="last-update">-</span>
                    </div>
                </div>
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
                    <h3>Iterations</h3>
                    <div class="value" id="iterations">-</div>
                </div>
            </div>
            
            <div class="content">
                <h2>Live Odds</h2>
                <div id="odds-table">
                    <p>Loading...</p>
                </div>
                <button class="refresh-btn" onclick="loadData()">Refresh Data</button>
            </div>
        </div>
        
        <script>
            function updateStatus(statusData) {
                const statusBadge = document.getElementById('status-badge');
                const lastUpdateEl = document.getElementById('last-update');
                const iterationsEl = document.getElementById('iterations');
                
                if (!statusData) {
                    statusBadge.textContent = 'unknown';
                    statusBadge.className = 'status-badge stuck';
                    lastUpdateEl.textContent = '-';
                    iterationsEl.textContent = '-';
                    return;
                }
                
                // Determine status
                let status = statusData.status || 'unknown';
                const lastUpdate = statusData.last_update ? new Date(statusData.last_update) : null;
                const now = new Date();
                
                // Check if stuck (last update older than 5 minutes)
                if (lastUpdate) {
                    const minutesSinceUpdate = (now - lastUpdate) / (1000 * 60);
                    if (minutesSinceUpdate > 5 && status === 'running') {
                        status = 'stuck';
                    }
                    // Format last update time
                    const hours = lastUpdate.getHours().toString().padStart(2, '0');
                    const minutes = lastUpdate.getMinutes().toString().padStart(2, '0');
                    const seconds = lastUpdate.getSeconds().toString().padStart(2, '0');
                    lastUpdateEl.textContent = `${hours}:${minutes}:${seconds}`;
                } else {
                    lastUpdateEl.textContent = '-';
                }
                
                // Update status badge
                statusBadge.textContent = status;
                statusBadge.className = `status-badge ${status}`;
                
                // Update iterations
                if (statusData.iterations !== undefined) {
                    iterationsEl.textContent = statusData.iterations;
                }
            }
            
            function loadData() {
                // Load status
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        updateStatus(data);
                    })
                    .catch(error => {
                        console.error('Error loading status:', error);
                    });
                
                // Load stats
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('total-events').textContent = data.total_events || 0;
                        document.getElementById('recent-signals').textContent = data.recent_signals || 0;
                        document.getElementById('avg-odds').textContent = data.avg_odds ? data.avg_odds.toFixed(2) : '-';
                        document.getElementById('matches-count').textContent = data.matches_count || 0;
                    })
                    .catch(error => {
                        console.error('Error loading stats:', error);
                    });
                
                // Load recent odds
                fetch('/api/recent-odds')
                    .then(response => response.json())
                    .then(data => {
                        const table = document.getElementById('odds-table');
                        if (data.length === 0) {
                            table.innerHTML = '<p>No recent odds data available.</p>';
                            return;
                        }
                        
                        // Group by match
                        const matchMap = {};
                        data.forEach(row => {
                            const matchKey = `${row.home_team || '-'} vs ${row.away_team || '-'}`;
                            if (!matchMap[matchKey]) {
                                matchMap[matchKey] = {
                                    home: row.home_team || '-',
                                    away: row.away_team || '-',
                                    bookmaker: row.bookmaker || '-',
                                    homeOdds: null,
                                    drawOdds: null,
                                    awayOdds: null
                                };
                            }
                            const outcome = row.outcome_name ? row.outcome_name.toLowerCase() : '';
                            if (outcome.includes('home') || outcome === '1') {
                                matchMap[matchKey].homeOdds = row.price ? row.price.toFixed(2) : '-';
                            } else if (outcome.includes('draw') || outcome === 'x') {
                                matchMap[matchKey].drawOdds = row.price ? row.price.toFixed(2) : '-';
                            } else if (outcome.includes('away') || outcome === '2') {
                                matchMap[matchKey].awayOdds = row.price ? row.price.toFixed(2) : '-';
                            }
                        });
                        
                        let html = '<table><thead><tr><th>Match</th><th>Home</th><th>Draw</th><th>Away</th><th>Bookmaker</th></tr></thead><tbody>';
                        Object.values(matchMap).forEach(match => {
                            html += `<tr>
                                <td>${match.home} vs ${match.away}</td>
                                <td>${match.homeOdds || '-'}</td>
                                <td>${match.drawOdds || '-'}</td>
                                <td>${match.awayOdds || '-'}</td>
                                <td>${match.bookmaker}</td>
                            </tr>`;
                        });
                        html += '</tbody></table>';
                        table.innerHTML = html;
                    })
                    .catch(error => {
                        console.error('Error loading odds:', error);
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
    
    @app.route('/api/status')
    def api_status():
        """API endpoint for engine status"""
        try:
            status_file = Path('data/status.json')
            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                return jsonify(status_data)
            else:
                return jsonify({
                    'status': 'unknown',
                    'last_update': None,
                    'iterations': 0,
                    'errors': 0
                })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats')
    def api_stats():
        """API endpoint for statistics"""
        try:
            conn = sqlite3.connect('data/odds.db')
            
            # Total events
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(DISTINCT home_team || away_team || commence_time) FROM odds')
            total_events = cursor.fetchone()[0] or 0
            
            # Count distinct matches (last 24 hours)
            cutoff = datetime.now() - timedelta(hours=24)
            cursor.execute('SELECT COUNT(DISTINCT home_team || away_team) FROM odds WHERE timestamp >= ?', (cutoff,))
            matches_count = cursor.fetchone()[0] or 0
            
            # Recent signals count (last hour)
            signals_file = 'data/signals.log'
            recent_signals = 0
            if os.path.exists(signals_file):
                cutoff = datetime.now() - timedelta(hours=1)
                with open(signals_file, 'r', encoding='utf-8', errors='replace') as f:
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
                'matches_count': matches_count,
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

