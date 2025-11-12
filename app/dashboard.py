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
    
    # Register /api/engine-status route for status.json (priority endpoint)
    @app.route('/api/engine-status', methods=['GET'])
    def api_engine_status():
        """API endpoint for engine status - reads from status.json"""
        try:
            status_file = Path('data/status.json')
            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8-sig') as f:
                    status_data = json.load(f)
                
                # Always return the status.json format (flat structure)
                return jsonify({
                    'status': status_data.get('status', 'unknown'),
                    'last_update': status_data.get('last_update'),
                    'iterations': status_data.get('iterations', 0),
                    'errors': status_data.get('errors', 0)
                })
            else:
                # Return default running status if file doesn't exist
                return jsonify({
                    'status': 'running',
                    'last_update': datetime.now(timezone.utc).isoformat(),
                    'iterations': 0,
                    'errors': 0
                })
        except Exception as e:
            # Return error status
            return jsonify({
                'status': 'error',
                'last_update': datetime.now(timezone.utc).isoformat(),
                'iterations': 0,
                'errors': 0,
                'error_message': str(e)
            }), 500
    
    # Register /api/status route - override any other status endpoint
    @app.route('/api/status', methods=['GET'])
    def api_status():
        """API endpoint for status - reads from status.json (takes precedence)"""
        try:
            status_file = Path('data/status.json')
            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8-sig') as f:
                    status_data = json.load(f)
                
                # Always return the status.json format (flat structure)
                # This overrides any other status endpoint
                return jsonify({
                    'status': status_data.get('status', 'unknown'),
                    'last_update': status_data.get('last_update'),
                    'iterations': status_data.get('iterations', 0),
                    'errors': status_data.get('errors', 0)
                })
            else:
                # Return default running status if file doesn't exist
                return jsonify({
                    'status': 'running',
                    'last_update': datetime.now(timezone.utc).isoformat(),
                    'iterations': 0,
                    'errors': 0
                })
        except Exception as e:
            # Return error status
            return jsonify({
                'status': 'error',
                'last_update': datetime.now(timezone.utc).isoformat(),
                'iterations': 0,
                'errors': 0,
                'error_message': str(e)
            }), 500
    
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
            .nav-link {
                cursor: pointer;
                user-select: none;
            }
            .view-section {
                display: none;
            }
            .view-section.active {
                display: block;
            }
            .refresh-btn:active {
                transform: scale(0.98);
            }
            .refresh-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .buy-signal-card {
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 5px;
            }
            .buy-signal-card h4 {
                color: #2e7d32;
                margin-bottom: 8px;
            }
            .buy-signal-card .odds-badge {
                background: #4caf50;
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                font-weight: bold;
                display: inline-block;
                margin-right: 10px;
            }
            .ignore-signal {
                opacity: 0.6;
            }
            .signal-buy {
                color: #4caf50;
                font-weight: bold;
            }
            .signal-ignore {
                color: #999;
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
            .status-badge.recovering {
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
                    <a href="#" class="nav-link active" data-view="analytics">Analytics</a>
                    <a href="#" class="nav-link" data-view="insights">Insights</a>
                    <a href="#" class="nav-link" data-view="signals">Signals</a>
                    <a href="#" class="nav-link" data-view="backtest">Backtest</a>
                    <a href="#" class="nav-link" data-view="reports">Reports</a>
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
            
            <div class="content view-section active" id="analytics-view">
                <h2>Live Odds</h2>
                <div id="odds-table">
                    <p>Loading...</p>
                </div>
                <button class="refresh-btn" id="refresh-btn">Refresh Data</button>
            </div>
            <div class="content view-section" id="insights-view">
                <h2>Insights</h2>
                <div id="insights-content">
                    <p>Insights and analytics coming soon...</p>
                </div>
            </div>
            <div class="content view-section" id="signals-view">
                <div style="margin-bottom: 20px;">
                    <h2 style="display: inline-block; margin-right: 20px;">💰 Bets to Place (BUY Signals)</h2>
                    <span id="buy-signals-count" style="background: #4caf50; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;"></span>
                </div>
                <div id="buy-signals-content" style="margin-bottom: 30px;">
                    <p>Loading BUY signals...</p>
                </div>
                <h3 style="margin-top: 30px; margin-bottom: 15px;">All Signals (BUY & IGNORE)</h3>
                <div id="signals-content">
                    <p>Loading all signals...</p>
                </div>
                <button class="refresh-btn" id="refresh-signals-btn" style="margin-top: 20px;">Refresh Signals</button>
            </div>
            <div class="content view-section" id="backtest-view">
                <h2>Backtest Results</h2>
                <div id="backtest-content">
                    <p>Backtest results will appear here...</p>
                </div>
            </div>
            <div class="content view-section" id="reports-view">
                <h2>Daily Reports</h2>
                <div id="reports-content">
                    <p>Daily reports will appear here...</p>
                </div>
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
                
                // Handle both nested and flat status structures
                let status = 'unknown';
                let lastUpdate = null;
                let lastUpdateTimestamp = null;
                const now = new Date();
                
                // PRIORITY: Use flat structure from status.json if available
                // Check if this is a flat structure (has last_update field and status is a string)
                if (statusData.last_update && typeof statusData.last_update === 'string' && 
                    statusData.status && typeof statusData.status === 'string') {
                    // Flat structure from status.json - this is the source of truth
                    // Always trust status.json status if it exists
                    status = statusData.status;
                    lastUpdateTimestamp = statusData.last_update;
                    
                    // If status.json says "running", trust it and don't override
                    // Only check if timestamp is stale to potentially mark as "stuck"
                    console.log('Using status.json status:', status, 'last_update:', lastUpdateTimestamp);
                } else if (statusData.status && typeof statusData.status === 'object') {
                    // Nested structure from collector - this is a fallback
                    // Only use if status.json is not available
                    console.warn('Received nested status structure, this should not happen if status.json exists');
                    const nestedStatus = statusData.status;
                    status = nestedStatus.status || 'unknown';
                    lastUpdateTimestamp = nestedStatus.last_successful_fetch || statusData.timestamp;
                    
                    // If status is "recovering" but updates are recent, consider it running
                    if (status === 'recovering' || nestedStatus.stuck_reason) {
                        if (lastUpdateTimestamp) {
                            try {
                                const updateTime = new Date(lastUpdateTimestamp.replace('Z', '+00:00'));
                                const minutesSinceUpdate = (now - updateTime) / (1000 * 60);
                                if (minutesSinceUpdate < 2) {
                                    status = 'running'; // Recent activity means system is running
                                } else {
                                    status = 'stuck';
                                }
                            } catch (e) {
                                status = 'stuck';
                            }
                        } else {
                            status = 'stuck';
                        }
                    }
                } else {
                    // Fallback: try to get status from any available field
                    status = (statusData.status && typeof statusData.status === 'string') ? statusData.status : 'running';
                    lastUpdateTimestamp = statusData.last_update || statusData.timestamp;
                }
                
                // Parse last update timestamp
                if (lastUpdateTimestamp) {
                    try {
                        // Handle different timestamp formats
                        let timestamp = lastUpdateTimestamp.toString();
                        // Replace Z with +00:00 for consistent parsing
                        timestamp = timestamp.replace('Z', '+00:00');
                        // If no timezone, assume UTC
                        if (!timestamp.includes('+') && !timestamp.includes('-', 10)) {
                            timestamp += '+00:00';
                        }
                        lastUpdate = new Date(timestamp);
                        
                        // Check if date is valid
                        if (isNaN(lastUpdate.getTime())) {
                            lastUpdate = null;
                        } else {
                            // Check if timestamp is stale (older than 5 minutes)
                            const minutesSinceUpdate = (now - lastUpdate) / (1000 * 60);
                            
                            // If status.json says "running", only override to "stuck" if timestamp is stale
                            // Always respect the status.json status if timestamp is fresh
                            if (status === 'running') {
                                if (minutesSinceUpdate > 5) {
                                    // Timestamp is stale, mark as stuck
                                    status = 'stuck';
                                    console.log('Status changed to stuck: timestamp is', minutesSinceUpdate.toFixed(1), 'minutes old');
                                } else {
                                    // Timestamp is fresh, keep as running
                                    status = 'running';
                                    console.log('Status is running: timestamp is', minutesSinceUpdate.toFixed(1), 'minutes old');
                                }
                            } else if (status === 'unknown' && minutesSinceUpdate > 5) {
                                // Unknown status with stale timestamp = stuck
                                status = 'stuck';
                            }
                            // Don't override "error" status - keep it as is
                            
                            // Format last update time (use local time for display)
                            const hours = lastUpdate.getHours().toString().padStart(2, '0');
                            const minutes = lastUpdate.getMinutes().toString().padStart(2, '0');
                            const seconds = lastUpdate.getSeconds().toString().padStart(2, '0');
                            lastUpdateEl.textContent = `${hours}:${minutes}:${seconds}`;
                        }
                    } catch (e) {
                        console.error('Error parsing last_update:', e);
                        lastUpdate = null;
                    }
                }
                
                if (!lastUpdate) {
                    lastUpdateEl.textContent = '-';
                    // If no last update and status is running, mark as stuck
                    if (status === 'running') {
                        status = 'stuck';
                    }
                }
                
                // Update status badge - ensure it reflects the final status
                statusBadge.textContent = status;
                statusBadge.className = `status-badge ${status}`;
                
                // Update iterations (only if available in flat structure)
                if (statusData.iterations !== undefined) {
                    iterationsEl.textContent = statusData.iterations;
                } else {
                    iterationsEl.textContent = '-';
                }
            }
            
            function loadData() {
                // Load status from engine-status endpoint (reads status.json)
                // This endpoint takes precedence and returns flat structure
                fetch('/api/engine-status')
                    .then(response => response.json())
                    .then(data => {
                        updateStatus(data);
                    })
                    .catch(error => {
                        console.error('Error loading engine status:', error);
                        // Fallback to /api/status
                        fetch('/api/status')
                            .then(response => response.json())
                            .then(data => {
                                updateStatus(data);
                            })
                            .catch(err => {
                                console.error('Error loading status:', err);
                            });
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
            
            // Navigation functionality
            document.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const view = this.getAttribute('data-view');
                    
                    // Remove active class from all nav links and views
                    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                    document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
                    
                    // Add active class to clicked link and corresponding view
                    this.classList.add('active');
                    const targetView = document.getElementById(view + '-view');
                    if (targetView) {
                        targetView.classList.add('active');
                    }
                    
                    // Load data for specific view if needed
                    if (view === 'signals') {
                        loadSignals(); // This loads both BUY signals and all signals
                    } else if (view === 'analytics') {
                        loadData();
                    }
                });
            });
            
            // Refresh button functionality
            const refreshBtn = document.getElementById('refresh-btn');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', function() {
                    this.disabled = true;
                    this.textContent = 'Refreshing...';
                    loadData();
                    setTimeout(() => {
                        this.disabled = false;
                        this.textContent = 'Refresh Data';
                    }, 1000);
                });
            }
            
            // Refresh signals button
            const refreshSignalsBtn = document.getElementById('refresh-signals-btn');
            if (refreshSignalsBtn) {
                refreshSignalsBtn.addEventListener('click', function() {
                    this.disabled = true;
                    this.textContent = 'Refreshing...';
                    loadSignals();
                    setTimeout(() => {
                        this.disabled = false;
                        this.textContent = 'Refresh Signals';
                    }, 1000);
                });
            }
            
            // Load BUY signals (bets to place)
            function loadBuySignals() {
                fetch('/api/buy-signals')
                    .then(response => response.json())
                    .then(data => {
                        const buySignalsContent = document.getElementById('buy-signals-content');
                        const buySignalsCount = document.getElementById('buy-signals-count');
                        
                        if (data.signals && data.signals.length > 0) {
                            buySignalsCount.textContent = `${data.count} BUY Signals`;
                            
                            let html = '';
                            data.signals.forEach(signal => {
                                html += `<div class="buy-signal-card">
                                    <h4>${signal.match || `${signal.home_team} vs ${signal.away_team}`}</h4>
                                    <div style="margin-bottom: 8px;">
                                        <span class="odds-badge">Odds: ${signal.odds ? signal.odds.toFixed(2) : '-'}</span>
                                        ${signal.outcome ? `<span style="background: #2196f3; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">${signal.outcome}</span>` : ''}
                                        ${signal.bookmaker ? `<span style="background: #ff9800; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; margin-left: 5px;">${signal.bookmaker}</span>` : ''}
                                    </div>
                                    <p style="margin: 5px 0; color: #666; font-size: 14px;">${signal.reason || 'High value bet'}</p>
                                    <p style="margin: 5px 0; color: #999; font-size: 12px;">🕐 ${signal.timestamp || 'Unknown time'}</p>
                                </div>`;
                            });
                            buySignalsContent.innerHTML = html;
                        } else {
                            buySignalsCount.textContent = '0 BUY Signals';
                            buySignalsContent.innerHTML = '<div style="padding: 20px; text-align: center; color: #999;"><p>No BUY signals available at the moment.</p><p style="font-size: 12px;">The system is analyzing odds and will show bets to place here when value opportunities are found.</p></div>';
                        }
                    })
                    .catch(error => {
                        console.error('Error loading BUY signals:', error);
                        document.getElementById('buy-signals-content').innerHTML = '<p style="color: #f44336;">Error loading BUY signals.</p>';
                    });
            }
            
            // Load all signals function
            function loadSignals() {
                // Load BUY signals
                loadBuySignals();
                
                // Load all signals (BUY and IGNORE)
                fetch('/api/all-signals')
                    .then(response => response.json())
                    .then(data => {
                        const signalsContent = document.getElementById('signals-content');
                        if (data.signals && data.signals.length > 0) {
                            // Create signals table
                            let html = '<table><thead><tr><th>Time</th><th>Match</th><th>Signal</th><th>Odds</th><th>Reason</th></tr></thead><tbody>';
                            data.signals.slice(0, 50).forEach(signal => {
                                const signalClass = signal.signal === 'BUY' ? 'signal-buy' : 'signal-ignore';
                                const rowClass = signal.signal === 'BUY' ? '' : 'ignore-signal';
                                html += `<tr class="${rowClass}">
                                    <td style="font-size: 12px;">${signal.timestamp ? signal.timestamp.split(' ')[1] || signal.timestamp : '-'}</td>
                                    <td>${signal.match || `${signal.home_team} vs ${signal.away_team}`}</td>
                                    <td><span class="${signalClass}">${signal.signal}</span></td>
                                    <td>${signal.odds ? signal.odds.toFixed(2) : '-'}</td>
                                    <td style="font-size: 12px; color: #666;">${signal.reason || '-'}</td>
                                </tr>`;
                            });
                            html += '</tbody></table>';
                            signalsContent.innerHTML = html;
                        } else {
                            signalsContent.innerHTML = '<p>No signals available.</p>';
                        }
                    })
                    .catch(error => {
                        console.error('Error loading signals:', error);
                        document.getElementById('signals-content').innerHTML = '<p>Error loading signals.</p>';
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
    
    @app.route('/api/buy-signals')
    def api_buy_signals():
        """API endpoint for BUY signals (bets to place)"""
        try:
            # Read signals from log file
            signals_file = Path('data/signals.log')
            buy_signals = []
            
            if signals_file.exists():
                with open(signals_file, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                    
                    # Parse last 100 lines (most recent signals)
                    for line in lines[-100:]:
                        if 'BUY' in line:
                            try:
                                # Parse log format: timestamp | match | BUY | reason | Odds: X.XX
                                parts = line.split(' | ')
                                if len(parts) >= 5:
                                    timestamp_str = parts[0].strip()
                                    match = parts[1].strip()
                                    signal = parts[2].strip()
                                    reason = parts[3].strip()
                                    odds_str = parts[4].replace('Odds:', '').strip()
                                    
                                    # Extract home and away teams
                                    if ' vs ' in match:
                                        home_team, away_team = match.split(' vs ', 1)
                                    else:
                                        home_team = match
                                        away_team = ''
                                    
                                    buy_signals.append({
                                        'timestamp': timestamp_str,
                                        'home_team': home_team,
                                        'away_team': away_team,
                                        'match': match,
                                        'signal': signal,
                                        'reason': reason,
                                        'odds': float(odds_str) if odds_str.replace('.', '').isdigit() else 0.0
                                    })
                            except Exception as e:
                                continue
            
            # Also check database for recent odds that might be BUY signals
            # This provides real-time BUY signals even if log hasn't been updated
            try:
                conn = sqlite3.connect('data/odds.db')
                cutoff = datetime.now() - timedelta(hours=1)
                
                query = '''
                    SELECT home_team, away_team, outcome_name, price, timestamp, bookmaker
                    FROM odds 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                '''
                
                df = pd.read_sql_query(query, conn, params=(cutoff,))
                conn.close()
                
                if not df.empty:
                    # Group by match and analyze for BUY signals
                    grouped = df.groupby(['home_team', 'away_team'])
                    
                    for (home_team, away_team), group in grouped:
                        outcome_odds = group.groupby('outcome_name')['price'].mean()
                        max_odds = outcome_odds.max()
                        std_odds = group.groupby('outcome_name')['price'].std().max()
                        
                        # BUY signal criteria: odds > 2.0 and low variance
                        if max_odds > 2.0 and (pd.isna(std_odds) or std_odds < 0.2):
                            # Check if we already have this signal from log
                            match_key = f"{home_team} vs {away_team}"
                            if not any(s['match'] == match_key for s in buy_signals):
                                # Get best bookmaker for this match
                                best_bookmaker = group.loc[group['price'].idxmax(), 'bookmaker']
                                best_outcome = group.loc[group['price'].idxmax(), 'outcome_name']
                                latest_timestamp = group['timestamp'].max()
                                
                                buy_signals.append({
                                    'timestamp': latest_timestamp,
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'match': match_key,
                                    'signal': 'BUY',
                                    'reason': f'High odds ({max_odds:.2f}) with low variance',
                                    'odds': float(max_odds),
                                    'outcome': best_outcome,
                                    'bookmaker': best_bookmaker
                                })
            except Exception as e:
                pass
            
            # Sort by timestamp (most recent first) and limit to 50
            buy_signals.sort(key=lambda x: x['timestamp'], reverse=True)
            buy_signals = buy_signals[:50]
            
            return jsonify({
                'signals': buy_signals,
                'count': len(buy_signals)
            })
        
        except Exception as e:
            return jsonify({'error': str(e), 'signals': [], 'count': 0}), 500
    
    @app.route('/api/all-signals')
    def api_all_signals():
        """API endpoint for all signals (BUY and IGNORE)"""
        try:
            signals_file = Path('data/signals.log')
            all_signals = []
            
            if signals_file.exists():
                with open(signals_file, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                    
                    # Parse last 200 lines
                    for line in lines[-200:]:
                        if ' | ' in line and ('BUY' in line or 'IGNORE' in line):
                            try:
                                parts = line.split(' | ')
                                if len(parts) >= 5:
                                    timestamp_str = parts[0].strip()
                                    match = parts[1].strip()
                                    signal = parts[2].strip()
                                    reason = parts[3].strip()
                                    odds_str = parts[4].replace('Odds:', '').strip()
                                    
                                    if ' vs ' in match:
                                        home_team, away_team = match.split(' vs ', 1)
                                    else:
                                        home_team = match
                                        away_team = ''
                                    
                                    all_signals.append({
                                        'timestamp': timestamp_str,
                                        'home_team': home_team,
                                        'away_team': away_team,
                                        'match': match,
                                        'signal': signal,
                                        'reason': reason,
                                        'odds': float(odds_str) if odds_str.replace('.', '').isdigit() else 0.0
                                    })
                            except Exception as e:
                                continue
            
            # Sort by timestamp (most recent first)
            all_signals.sort(key=lambda x: x['timestamp'], reverse=True)
            all_signals = all_signals[:100]
            
            return jsonify({
                'signals': all_signals,
                'count': len(all_signals),
                'buy_count': len([s for s in all_signals if s['signal'] == 'BUY'])
            })
        
        except Exception as e:
            return jsonify({'error': str(e), 'signals': [], 'count': 0}), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)

