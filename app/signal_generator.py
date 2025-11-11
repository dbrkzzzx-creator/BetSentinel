"""
Signal Generator - Analyzes odds and generates BUY/IGNORE signals
"""
import sqlite3
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_recent_odds(hours=1):
    """Get recent odds from database"""
    try:
        conn = sqlite3.connect('data/odds.db')
        
        # Get odds from the last N hours
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        query = '''
            SELECT * FROM odds 
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(cutoff_time,))
        return df
    
    except sqlite3.OperationalError as e:
        logger.error(f"Database error fetching recent odds: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching recent odds: {e}")
        return pd.DataFrame()
    finally:
        try:
            conn.close()
        except:
            pass

def analyze_odds(df):
    """Analyze odds data and generate signals"""
    if df.empty:
        logger.warning("No odds data to analyze")
        return []
    
    signals = []
    
    try:
        # Group by event (home_team + away_team + commence_time)
        grouped = df.groupby(['home_team', 'away_team', 'commence_time'])
        
        for (home_team, away_team, commence_time), group in grouped:
            # Calculate average odds for each outcome
            outcome_odds = group.groupby('outcome_name')['price'].mean()
            
            # Simple signal logic: BUY if we find value (odds > 2.0 and consistent across bookmakers)
            # This is a basic example - you can implement more sophisticated logic
            
            max_odds = outcome_odds.max()
            min_odds = outcome_odds.min()
            std_odds = group.groupby('outcome_name')['price'].std().max()
            
            # Signal: BUY if odds are high (>2.0) and relatively stable (low std)
            if max_odds > 2.0 and (std_odds < 0.2 or pd.isna(std_odds)):
                signal = "BUY"
                reason = f"High odds ({max_odds:.2f}) with low variance"
            else:
                signal = "IGNORE"
                reason = f"Odds {max_odds:.2f} don't meet criteria"
            
            signals.append({
                'home_team': home_team,
                'away_team': away_team,
                'commence_time': commence_time,
                'signal': signal,
                'reason': reason,
                'max_odds': max_odds,
                'min_odds': min_odds,
                'timestamp': datetime.now()
            })
            
            logger.info(f"Signal for {home_team} vs {away_team}: {signal} - {reason}")
    
    except Exception as e:
        logger.error(f"Error analyzing odds: {e}")
    
    return signals

def log_signals(signals):
    """Log signals to file"""
    if not signals:
        return
    
    log_file = 'data/signals.log'
    
    with open(log_file, 'a') as f:
        for signal in signals:
            f.write(f"{signal['timestamp']} | {signal['home_team']} vs {signal['away_team']} | "
                   f"{signal['signal']} | {signal['reason']} | "
                   f"Odds: {signal['max_odds']:.2f}\n")
    
    logger.info(f"Logged {len(signals)} signals to {log_file}")

def generate_signals():
    """Main function to generate signals"""
    logger.info("Starting signal generation...")
    
    # Get recent odds (last hour)
    df = get_recent_odds(hours=1)
    
    if df.empty:
        logger.warning("No recent odds data available for signal generation")
        return
    
    # Analyze and generate signals
    signals = analyze_odds(df)
    
    # Log signals
    if signals:
        log_signals(signals)
        logger.info(f"Generated {len(signals)} signals")
        logger.info("Signal generated")
    else:
        logger.info("No signals generated")

if __name__ == "__main__":
    # Test the signal generator
    generate_signals()

