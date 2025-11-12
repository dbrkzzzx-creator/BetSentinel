"""
Data Tools - Utilities for data processing and analysis
"""
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

def load_json_file(file_path: Path) -> Optional[Dict]:
    """Load JSON file safely"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return None

def save_json_file(file_path: Path, data: Dict):
    """Save JSON file safely"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

def aggregate_odds_data(df: pd.DataFrame) -> Dict:
    """Aggregate odds data for analysis"""
    if df.empty:
        return {}
    
    return {
        "total_events": len(df.groupby(['home_team', 'away_team'])),
        "avg_odds": float(df['price'].mean()) if 'price' in df.columns else 0.0,
        "max_odds": float(df['price'].max()) if 'price' in df.columns else 0.0,
        "min_odds": float(df['price'].min()) if 'price' in df.columns else 0.0,
    }

