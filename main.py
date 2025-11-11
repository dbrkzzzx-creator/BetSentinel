"""
Main entry point for BetSentinel
Starts scheduled jobs and Flask dashboard
"""
import os
import threading
import time
from dotenv import load_dotenv
import schedule
import logging

from app.collector import collect_odds
from app.signal_generator import generate_signals
from app.backtester import run_backtest
from app.reporter import generate_daily_report
from app.dashboard import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def update_status_file():
    """Update status.json file to keep it fresh"""
    try:
        status_file = Path('data/status.json')
        status_data = {
            "status": "running",
            "last_update": datetime.now(timezone.utc).isoformat(),
            "iterations": 0,
            "errors": 0
        }
        
        # Load existing status if it exists to preserve iterations and errors
        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    status_data['iterations'] = existing.get('iterations', 0)
                    status_data['errors'] = existing.get('errors', 0)
            except:
                pass
        
        # Write updated status
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Failed to update status.json: {e}")

def run_scheduler():
    """Run scheduled jobs"""
    # Schedule collector to run every 60 seconds
    schedule.every(60).seconds.do(collect_odds)
    
    # Schedule signal generator to run every 5 minutes
    schedule.every(5).minutes.do(generate_signals)
    
    # Schedule backtester to run every hour
    schedule.every().hour.do(run_backtest)
    
    # Schedule reporter to run daily at midnight
    schedule.every().day.at("00:00").do(generate_daily_report)
    
    # Schedule status update every 2 minutes to keep it fresh
    schedule.every(2).minutes.do(update_status_file)
    
    logger.info("Scheduler started with jobs configured")
    
    # Update status file on startup
    update_status_file()
    
    # Run initial jobs
    logger.info("Running initial jobs...")
    collect_odds()
    generate_signals()
    
    # Keep scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_dashboard():
    """Run Flask dashboard in a separate thread"""
    app = create_app()
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Flask dashboard on {host}:{port}")
    app.run(host=host, port=port, debug=debug, use_reloader=False)

def main():
    """Main entry point"""
    logger.info("Starting BetSentinel...")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Start Flask dashboard in background thread
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    
    # Give Flask a moment to start
    time.sleep(2)
    
    # Run scheduler in main thread
    try:
        run_scheduler()
    except KeyboardInterrupt:
        logger.info("Shutting down BetSentinel...")
        raise

if __name__ == "__main__":
    main()

