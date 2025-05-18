import os

# project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#log files
LOG_FILE = os.path.join(BASE_DIR, "logs", "logs.txt")
ALERT_FILE = os.path.join(BASE_DIR, "logs", "alert_logs.txt")
CLIPBOARD_LOG_FILE = os.path.join(BASE_DIR, "logs", "clipboard_logs.txt")

# Screenshot
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'static', 'screens')  


# Model file
MODEL_FILE = os.path.join(BASE_DIR, "suspicious_classifier.pkl")
print(ALERT_FILE)