"""
Odds Collector - Fetches live odds from The Odds API (Optimized)
"""
import os
import requests
import sqlite3
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from app.performance_tracker import track_performance, record_api_latency
from app.cache import get_cached_odds, cache_odds, is_cache_valid

load_dotenv()

logger = logging.getLogger(__name__)

ODDS_API_KEY = os.getenv('ODDS_API_KEY')
ODDS_API_BASE_URL = 'https://api.the-odds-api.com/v4'

def init_database():
    """Initialize SQLite database with odds table"""
    conn = sqlite3.connect('data/odds.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS odds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport_key TEXT,
            sport_title TEXT,
            home_team TEXT,
            away_team TEXT,
            commence_time TEXT,
            bookmaker TEXT,
            market TEXT,
            outcome_name TEXT,
            price REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized")

def fetch_odds():
    """Fetch odds from The Odds API with caching"""
    if not ODDS_API_KEY or ODDS_API_KEY == 'your_api_key_here':
        logger.warning("ODDS_API_KEY not set in .env file")
        return None
    
    try:
        # Fetch soccer odds (soccer is the sport key for football)
        url = f"{ODDS_API_BASE_URL}/sports/soccer/odds"
        params = {
            'apiKey': ODDS_API_KEY,
            'regions': 'uk',
            'markets': 'h2h',
            'oddsFormat': 'decimal'
        }
        
        # Check cache first
        cached_data = get_cached_odds(url, params)
        if cached_data and is_cache_valid(url, params, max_age_seconds=30):
            logger.info(f"Using cached odds data ({len(cached_data['data'])} events)")
            return cached_data['data']
        
        # Measure API latency
        start_time = time.time()
        response = requests.get(url, params=params, timeout=10)
        api_latency = time.time() - start_time
        response.raise_for_status()
        
        # Record API latency
        record_api_latency('collector', api_latency)
        
        data = response.json()
        
        # Cache the data
        cache_odds(url, params, data)
        
        logger.info(f"Fetched {len(data)} events from The Odds API (latency: {api_latency:.3f}s)")
        return data
    
    except requests.exceptions.Timeout:
        logger.error("Timeout while fetching odds from API")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Connection error while fetching odds - check internet connection")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching odds: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in fetch_odds: {e}")
        return None

def store_odds(odds_data):
    """Store odds data in SQLite database with batch inserts and I/O tracking"""
    if not odds_data:
        return
    
    import time
    from app.performance_tracker import record_metrics
    
    io_start = time.time()
    conn = sqlite3.connect('data/odds.db')
    cursor = conn.cursor()
    
    try:
        # Prepare batch data
        batch_data = []
        for event in odds_data:
            sport_key = event.get('sport_key', 'soccer')
            sport_title = event.get('sport_title', 'Soccer')
            home_team = event.get('home_team', '')
            away_team = event.get('away_team', '')
            commence_time = event.get('commence_time', '')
            
            bookmakers = event.get('bookmakers', [])
            
            for bookmaker in bookmakers:
                bookmaker_name = bookmaker.get('key', '')
                markets = bookmaker.get('markets', [])
                
                for market in markets:
                    market_key = market.get('key', '')
                    outcomes = market.get('outcomes', [])
                    
                    for outcome in outcomes:
                        outcome_name = outcome.get('name', '')
                        price = outcome.get('price', 0.0)
                        
                        batch_data.append((
                            sport_key, sport_title, home_team, away_team,
                            commence_time, bookmaker_name, market_key,
                            outcome_name, price
                        ))
        
        # Batch insert for better performance
        if batch_data:
            cursor.executemany('''
                INSERT INTO odds 
                (sport_key, sport_title, home_team, away_team, 
                 commence_time, bookmaker, market, outcome_name, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', batch_data)
        
        conn.commit()
        io_wait_time = time.time() - io_start
        
        # Record I/O wait time
        record_metrics(
            module_name='collector',
            function_name='store_odds',
            runtime=0,
            cpu_usage=0,
            memory_usage=0,
            io_wait_time=io_wait_time
        )
        
        logger.info(f"Stored {len(batch_data)} odds records for {len(odds_data)} events (batch insert, I/O: {io_wait_time:.3f}s)")
    
    except Exception as e:
        logger.error(f"Error storing odds: {e}")
        conn.rollback()
    
    finally:
        conn.close()

@track_performance('collector')
def collect_odds():
    """Main function to collect and store odds"""
    logger.info("Collector started")
    logger.info("Starting odds collection...")
    
    # Ensure database is initialized
    init_database()
    
    # Fetch odds from API
    odds_data = fetch_odds()
    
    # Store in database
    if odds_data:
        store_odds(odds_data)
        logger.info("Odds collection completed successfully")
    else:
        logger.warning("No odds data to store")

if __name__ == "__main__":
    # Test the collector
    collect_odds()

