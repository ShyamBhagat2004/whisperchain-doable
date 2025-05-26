from datetime import datetime

LOG_FILE = "logs.txt"

# log a single event: simply what role did what action and when it did that action
def log_event(role, action):
    now = datetime.utcnow().isoformat() #found a way to get time without timezones or anything
    log_line = f"{now} | ROLE: {role} | ACTION: {action}\n"
#used try except sinc sometimes errorrs were happening, but not anymore I think
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_line)
    except Exception as e:
        print("logging failed for some reason:", e)

# read all logs (just for moderators or sysadmins, not directly required or anything)
def read_all_logs():
    try:
        with open(LOG_FILE, "r") as f:
            logs = f.readlines()
        return logs
    except FileNotFoundError:
        print("no log file yet, it has not been created")
        return []
