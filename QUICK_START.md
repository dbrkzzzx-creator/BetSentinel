# BetSentinel Dashboard - Quick Start Guide

## 🚀 One-Click Start

Simply run:
```bash
run_dashboard.bat
```

This will automatically:
1. Start Flask backend on port 5000
2. Start Next.js frontend on port 3000
3. Open both in separate windows

## 📍 URLs

- **Main Dashboard**: http://localhost:3000
- **Automation Page**: http://localhost:3000/automation
- **Backend API**: http://localhost:5000

## 🔧 Manual Start (if needed)

### Backend
```bash
cd D:\AI\BetSentinel
venv\Scripts\activate
python app.py
```

### Frontend
```bash
cd D:\AI\BetSentinel\frontend
npm install  # First time only
npm run dev
```

## ✅ Verification

1. Check backend: http://localhost:5000/api/status
   - Should return JSON with status

2. Check frontend: http://localhost:3000
   - Should show dashboard with status badge

3. Check automation: http://localhost:3000/automation
   - Should show automation controls and log viewer

## 🎯 Features

### Dashboard (`/`)
- Real-time status display
- Live events with odds
- Auto-refresh every 30 seconds

### Automation (`/automation`)
- Rule editor (min/max bet, daily cap, whitelist/blacklist)
- Start/Stop automation controls
- Live activity log (updates every 10 seconds)
- Toast notifications for actions

## 🐛 Troubleshooting

**Port 3000 in use?**
- The frontend will automatically try port 3000
- If blocked, Next.js will suggest an alternative port

**Backend not starting?**
- Ensure Flask-Cors is installed: `pip install Flask-Cors`
- Check port 5000 is not in use

**Frontend not connecting?**
- Verify backend is running on port 5000
- Check browser console for CORS errors
- Ensure both servers are running

## 📝 API Endpoints

- `GET /api/status` - System status
- `GET /api/events` - Mock betting events
- `GET /api/automation/status` - Automation status
- `GET /api/automation/rules` - Get automation rules
- `POST /api/automation/rules` - Save automation rules
- `POST /api/automation/start` - Start automation
- `POST /api/automation/stop` - Stop automation
- `GET /api/automation/logs` - Get activity logs

