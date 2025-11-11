# Autonomous Project Engineer - BetSentinel

## Overview

The Autonomous Project Engineer (`autonomous_engine.py`) continuously builds, tests, and perfects the BetSentinel system until it runs for 24 hours without errors.

## How It Works

The autonomous engine operates in a continuous loop:

1. **Task Selection**: Reads next unfinished task from `roadmap.json` or scans source for TODO comments
2. **Code Modification**: Generates or modifies Python code as needed
3. **Testing**: Runs `python main.py` and captures output
4. **Error Detection**: Parses console output, `app.log`, and tracebacks for errors
5. **Auto-Fix**: Attempts to fix errors by regenerating problematic functions/classes
6. **Success Verification**: Checks for required success log messages
7. **Git Commit**: Commits and pushes progress automatically
8. **State Tracking**: Saves progress to `system/state.json`
9. **24h Checkpoint**: After 24 hours, compresses logs and creates checkpoint

## Running the Autonomous Engine

### Prerequisites

1. Ensure virtual environment is set up:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure `.env` file with your API key

3. Initialize git repository (if not already):
   ```bash
   git init
   git remote add origin https://github.com/dbrkzzzx-creator/BetSentinel.git
   ```

### Start the Engine

```bash
python autonomous_engine.py
```

The engine will:
- Run continuously until project is marked complete
- Auto-commit every iteration
- Handle errors automatically
- Track progress in `system/state.json`

## Completion Criteria

The project is considered complete when:

- ✅ Two consecutive 24-hour runs with zero runtime errors
- ✅ Dashboard reachable at `http://127.0.0.1:5000`
- ✅ All modules emit required success logs:
  - "Collector started"
  - "Signal generated"
  - "Backtest complete"
  - "Report generated"
- ✅ Final commit message: "✅ Project stable: BetSentinel ready"

## State Management

The engine saves state to `system/state.json`:
- Current stage and task
- Iteration count
- Last commit hash
- Error history
- Success metrics

## Safety Features

- Never modifies files outside `D:\AI\BetSentinel`
- Never exposes or changes `.env` contents
- Never halts unless `project_complete: true` in state.json
- Resumes automatically on restart from latest state

## Monitoring

Watch the console output for:
- Iteration numbers
- Current tasks
- Error detection and fixes
- Success verification
- Git commit confirmations

## Manual Intervention

To stop the engine:
- Press `Ctrl+C` (saves state before exiting)
- Or set `"project_complete": true` in `system/state.json`

## Files

- `autonomous_engine.py` - Main autonomous engine
- `roadmap.json` - Task roadmap
- `system/state.json` - Progress tracking
- `data/app.log` - Application logs (checked for success messages)

