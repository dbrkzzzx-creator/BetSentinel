import time, os, json

def tail_log(path, lines=10):
    if not os.path.exists(path):
        return f"[No log found: {path}]"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return "".join(f.readlines()[-lines:])

def check():
    log = tail_log("data/engine_run.log")
    print("=== BetSentinel Status ===")
    print(f"Checked: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("==========================")
    print(log)
    print("==========================")
    print("Active processes:")
    os.system('tasklist | find "python"')

if __name__ == "__main__":
    check()
