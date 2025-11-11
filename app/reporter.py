"""
Reporter - Generates daily reports with charts and summaries
"""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

def get_daily_data():
    """Get data from the last 24 hours"""
    conn = sqlite3.connect('data/odds.db')
    
    try:
        cutoff_time = datetime.now() - timedelta(days=1)
        
        query = '''
            SELECT * FROM odds 
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        '''
        
        df = pd.read_sql_query(query, conn, params=(cutoff_time,))
        return df
    
    except Exception as e:
        logger.error(f"Error fetching daily data: {e}")
        return pd.DataFrame()
    
    finally:
        conn.close()

def read_signals_log():
    """Read signals from log file"""
    signals_file = 'data/signals.log'
    
    if not os.path.exists(signals_file):
        return []
    
    signals = []
    try:
        with open(signals_file, 'r') as f:
            lines = f.readlines()
            # Get last 24 hours of signals
            cutoff = datetime.now() - timedelta(days=1)
            
            for line in lines:
                if line.strip():
                    parts = line.split(' | ')
                    if len(parts) >= 4:
                        try:
                            signal_time = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S.%f')
                            if signal_time >= cutoff:
                                signals.append(line.strip())
                        except ValueError:
                            continue
    
    except Exception as e:
        logger.error(f"Error reading signals log: {e}")
    
    return signals

def generate_charts(df):
    """Generate matplotlib charts"""
    if df.empty:
        logger.warning("No data available for charts")
        return
    
    try:
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Daily BetSentinel Report', fontsize=16, fontweight='bold')
        
        # Convert timestamp to datetime if needed
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Chart 1: Odds distribution over time
        ax1 = axes[0, 0]
        if 'timestamp' in df.columns and 'price' in df.columns:
            df_sampled = df.groupby(df['timestamp'].dt.floor('H'))['price'].mean()
            ax1.plot(df_sampled.index, df_sampled.values, marker='o', linewidth=2)
            ax1.set_title('Average Odds Over Time')
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Average Odds')
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Chart 2: Odds histogram
        ax2 = axes[0, 1]
        if 'price' in df.columns:
            ax2.hist(df['price'], bins=30, edgecolor='black', alpha=0.7)
            ax2.set_title('Odds Distribution')
            ax2.set_xlabel('Odds')
            ax2.set_ylabel('Frequency')
            ax2.grid(True, alpha=0.3)
        
        # Chart 3: Events by bookmaker
        ax3 = axes[1, 0]
        if 'bookmaker' in df.columns:
            bookmaker_counts = df['bookmaker'].value_counts().head(10)
            ax3.barh(bookmaker_counts.index, bookmaker_counts.values)
            ax3.set_title('Top 10 Bookmakers by Event Count')
            ax3.set_xlabel('Number of Events')
            ax3.grid(True, alpha=0.3, axis='x')
        
        # Chart 4: Events by outcome
        ax4 = axes[1, 1]
        if 'outcome_name' in df.columns:
            outcome_counts = df['outcome_name'].value_counts()
            ax4.pie(outcome_counts.values, labels=outcome_counts.index, autopct='%1.1f%%')
            ax4.set_title('Outcome Distribution')
        
        plt.tight_layout()
        
        # Save chart
        chart_path = 'data/daily_report.png'
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Charts saved to {chart_path}")
        return chart_path
    
    except Exception as e:
        logger.error(f"Error generating charts: {e}")
        return None

def generate_summary(df, signals):
    """Generate text summary"""
    summary = []
    summary.append("=" * 60)
    summary.append("BETSENTINEL DAILY REPORT")
    summary.append("=" * 60)
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("")
    
    if df.empty:
        summary.append("No odds data available for the last 24 hours.")
    else:
        summary.append("ODDS STATISTICS:")
        summary.append(f"  Total records: {len(df)}")
        summary.append(f"  Unique events: {df.groupby(['home_team', 'away_team', 'commence_time']).ngroups}")
        summary.append(f"  Average odds: {df['price'].mean():.2f}")
        summary.append(f"  Min odds: {df['price'].min():.2f}")
        summary.append(f"  Max odds: {df['price'].max():.2f}")
        summary.append(f"  Unique bookmakers: {df['bookmaker'].nunique()}")
        summary.append("")
    
    summary.append("SIGNALS GENERATED:")
    summary.append(f"  Total signals in last 24h: {len(signals)}")
    
    buy_count = sum(1 for s in signals if 'BUY' in s)
    ignore_count = sum(1 for s in signals if 'IGNORE' in s)
    
    summary.append(f"  BUY signals: {buy_count}")
    summary.append(f"  IGNORE signals: {ignore_count}")
    summary.append("")
    
    summary.append("=" * 60)
    
    return "\n".join(summary)

def generate_daily_report():
    """Main function to generate daily report"""
    logger.info("Starting daily report generation...")
    
    # Get daily data
    df = get_daily_data()
    
    # Get signals
    signals = read_signals_log()
    
    # Generate charts
    chart_path = generate_charts(df)
    
    # Generate summary
    summary = generate_summary(df, signals)
    
    # Write report to file
    report_file = 'data/report.txt'
    with open(report_file, 'w') as f:
        f.write(summary)
        if chart_path:
            f.write(f"\n\nChart saved to: {chart_path}\n")
    
    logger.info(f"Daily report saved to {report_file}")
    logger.info("Report generated")
    logger.info(summary)

if __name__ == "__main__":
    # Test the reporter
    generate_daily_report()

