# BetSentinel Full-Stack Dashboard Setup

## Quick Start

### 1. Install Backend Dependencies

```bash
cd D:\AI\BetSentinel
venv\Scripts\activate
pip install Flask-Cors numpy gunicorn
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Run Backend

In one terminal:
```bash
cd D:\AI\BetSentinel
venv\Scripts\activate
python app.py
```

The Flask API will run on `http://localhost:5000`

### 4. Run Frontend

In another terminal:
```bash
cd D:\AI\BetSentinel\frontend
npm run dev
```

The Next.js dashboard will run on `http://localhost:3000`

## Project Structure

```
D:\AI\BetSentinel\
├── app/
│   ├── routes/          # Flask API routes
│   │   ├── events.py    # /api/events endpoint
│   │   ├── rules.py     # /api/rules endpoint
│   │   └── status.py    # /api/status endpoint
│   ├── utils/           # Utility modules
│   │   ├── cache.py
│   │   ├── betting_engine.py
│   │   └── data_tools.py
│   └── templates/
├── frontend/            # Next.js + Tailwind frontend
│   ├── pages/
│   │   └── index.tsx    # Main dashboard page
│   ├── styles/
│   └── package.json
├── app.py               # Flask application entry point
├── main.py              # Original BetSentinel entry point
└── requirements.txt
```

## API Endpoints

- `GET /api/status` - Get system status from data/status.json
- `GET /api/events` - Get mock betting events
- `GET /api/rules` - Get betting rules
- `POST /api/rules` - Save betting rules

## Notes

- The new `app.py` runs alongside the existing `main.py` (which uses `app/dashboard.py`)
- Both can run simultaneously on different ports if needed
- The Next.js frontend connects to the Flask API at localhost:5000
- CORS is enabled to allow frontend-backend communication

