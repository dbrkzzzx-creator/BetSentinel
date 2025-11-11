"""
Backtester - Runs backtests on stored odds data
"""
import sqlite3
import pandas as pd
import logging
from datetime import datetime, timedelta
import json
from app.performance_tracker import track_performance

logger = logging.getLogger(__name__)

def get_historical_odds(days=7):
    """Get historical odds from database"""
    conn = sqlite3.connect('data/odds.db')
    
    try:
        cutoff_time = datetime.now() - timedelta(days=days)
        
        query = '''
            SELECT * FROM odds 
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(cutoff_time,))
        return df
    
    except Exception as e:
        logger.error(f"Error fetching historical odds: {e}")
        return pd.DataFrame()
    
    finally:
        conn.close()

def calculate_metrics(df):
    """Calculate backtest performance metrics"""
    if df.empty:
        return None
    
    metrics = {
        'total_events': 0,
        'total_signals': 0,
        'buy_signals': 0,
        'ignore_signals': 0,
        'avg_odds': 0.0,
        'max_odds': 0.0,
        'min_odds': 0.0,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Group by event
        grouped = df.groupby(['home_team', 'away_team', 'commence_time'])
        metrics['total_events'] = len(grouped)
        
        # Calculate odds statistics
        if 'price' in df.columns:
            metrics['avg_odds'] = float(df['price'].mean())
            metrics['max_odds'] = float(df['price'].max())
            metrics['min_odds'] = float(df['price'].min())
        
        # Simulate signal generation for backtesting
        buy_count = 0
        ignore_count = 0
        
        for (home_team, away_team, commence_time), group in grouped:
            outcome_odds = group.groupby('outcome_name')['price'].mean()
            max_odds = outcome_odds.max()
            
            if max_odds > 2.0:
                buy_count += 1
            else:
                ignore_count += 1
        
        metrics['buy_signals'] = buy_count
        metrics['ignore_signals'] = ignore_count
        metrics['total_signals'] = buy_count + ignore_count
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
    
    return metrics

def save_metrics(metrics):
    """Save performance metrics to file"""
    if not metrics:
        return
    
    metrics_file = 'data/backtest_metrics.json'
    
    # Load existing metrics if file exists
    try:
        with open(metrics_file, 'r') as f:
            all_metrics = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_metrics = []
    
    # Append new metrics
    all_metrics.append(metrics)
    
    # Keep only last 100 entries
    if len(all_metrics) > 100:
        all_metrics = all_metrics[-100:]
    
    # Save back to file
    with open(metrics_file, 'w') as f:
        json.dump(all_metrics, f, indent=2)
    
    logger.info(f"Saved metrics to {metrics_file}")

@track_performance('backtester')
def run_backtest():
    """Main function to run backtest"""
    logger.info("Starting backtest...")
    
    # Get historical odds (last 7 days)
    df = get_historical_odds(days=7)
    
    if df.empty:
        logger.warning("No historical odds data available for backtesting")
        return
    
    # Calculate metrics
    metrics = calculate_metrics(df)
    
    if metrics:
        save_metrics(metrics)
        logger.info(f"Backtest completed: {metrics['total_events']} events, "
                   f"{metrics['buy_signals']} BUY signals, "
                   f"{metrics['ignore_signals']} IGNORE signals")
        logger.info("Backtest complete")
    else:
        logger.warning("No metrics calculated")

if __name__ == "__main__":
    # Test the backtester
    run_backtest()

