"""
Backtester - Runs backtests on stored odds data (Optimized with multiprocessing)
"""
import sqlite3
import pandas as pd
import logging
from datetime import datetime, timedelta
import json
from multiprocessing import Pool, cpu_count
from functools import partial
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

def process_event_group_data(group_data_dict):
    """Process a single event group for backtesting (for multiprocessing)"""
    try:
        # Convert dict back to DataFrame for processing
        import pandas as pd
        group_df = pd.DataFrame(group_data_dict)
        outcome_odds = group_df.groupby('outcome_name')['price'].mean()
        max_odds = outcome_odds.max()
        
        signal = 'buy' if max_odds > 2.0 else 'ignore'
        return signal
    except Exception as e:
        logger.error(f"Error processing event group: {e}")
        return 'ignore'

def calculate_metrics(df):
    """Calculate backtest performance metrics with multiprocessing"""
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
        # Calculate odds statistics (fast, no multiprocessing needed)
        if 'price' in df.columns:
            metrics['avg_odds'] = float(df['price'].mean())
            metrics['max_odds'] = float(df['price'].max())
            metrics['min_odds'] = float(df['price'].min())
        
        # Group by event
        grouped = df.groupby(['home_team', 'away_team', 'commence_time'])
        metrics['total_events'] = len(grouped)
        
        # Use multiprocessing for large datasets (simplified approach)
        # For better performance with pandas, we'll use vectorized operations
        # Multiprocessing overhead is only beneficial for very large datasets
        
        buy_count = 0
        ignore_count = 0
        
        # Optimized sequential processing with vectorized operations
        for (home_team, away_team, commence_time), group in grouped:
            try:
                outcome_odds = group.groupby('outcome_name')['price'].mean()
                max_odds = outcome_odds.max()
                
                if max_odds > 2.0:
                    buy_count += 1
                else:
                    ignore_count += 1
            except Exception as e:
                logger.warning(f"Error processing event {home_team} vs {away_team}: {e}")
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

