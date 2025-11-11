# BetSentinel - Football Exchange Agent

A Python-based football exchange agent that collects odds, generates trading signals, and provides analytics through a web dashboard.

## Features

- **Live Odds Collection**: Fetches odds from The Odds API every 60 seconds
- **Signal Generation**: Analyzes odds and generates BUY/IGNORE signals every 5 minutes
- **Backtesting**: Runs hourly backtests on historical data
- **Daily Reports**: Generates daily reports with charts and summaries
- **Web Dashboard**: Flask-based dashboard for real-time monitoring

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
ODDS_API_KEY=your_api_key_here
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=True
```

Get your API key from [The Odds API](https://the-odds-api.com/).

### 3. Run the Application

```bash
python main.py
```

The application will:
- Start the Flask dashboard at `http://127.0.0.1:5000`
- Begin collecting odds every 60 seconds
- Generate signals every 5 minutes
- Run backtests every hour
- Generate daily reports at midnight

## Project Structure

```
BetSentinel/
├── app/
│   ├── __init__.py
│   ├── collector.py          # Odds collection from API
│   ├── signal_generator.py    # Signal analysis and generation
│   ├── backtester.py          # Backtesting engine
│   ├── reporter.py            # Daily report generation
│   └── dashboard.py           # Flask web dashboard
├── data/
│   ├── odds.db                # SQLite database (created automatically)
│   ├── signals.log            # Signal log file
│   ├── backtest_metrics.json  # Backtest results
│   ├── daily_report.png       # Daily report charts
│   ├── report.txt             # Daily report summary
│   └── app.log                # Application log
├── .env                       # Environment variables (create this)
├── requirements.txt           # Python dependencies
└── main.py                    # Main entry point
```

## Usage

### Dashboard

Access the web dashboard at `http://127.0.0.1:5000` to view:
- Real-time statistics
- Recent odds data
- System status

### Logs

All activity is logged to:
- Console output
- `data/app.log` file

### Reports

Daily reports are generated automatically at midnight and saved to:
- `data/report.txt` - Text summary
- `data/daily_report.png` - Visual charts

## Autonomous Project Engineer

BetSentinel includes an autonomous engineering system that continuously tests and improves the codebase. See [AUTONOMOUS_ENGINE.md](AUTONOMOUS_ENGINE.md) for details.

To run the autonomous engine:

```bash
python autonomous_engine.py
```

The engine will:
- Continuously test the system
- Auto-fix errors
- Commit progress to git
- Run until the system is stable for 24+ hours

## Requirements

- Python 3.12+
- The Odds API key
- Internet connection for API calls

## License

MIT

