
# Keylogger Suspicious Activity Monitoring System

- A Python-based tool to detect and log suspicious user activity.

# Features:
- Real-time keylogging (keyboard monitoring)
- Clipboard content monitoring
- Suspicious sentence detection using a machine learning model (TF-IDF + Naive Bayes)
- Alert logging with timestamps and confidence scores
- Automatic screenshot capture when suspicious text is detected
- Web dashboard (Flask + HTML/CSS) to view logs and flagged sentences

# Project Structure:
- /app/ → Flask dashboard backend + HTML templates + CSS
- /logs/ → Logs of all keystrokes and suspicious activities
- /screens/ → Screenshots taken at detection time
- detection.py → Suspicious text detection logic
- security.py → Main keylogger and clipboard monitor
- suspicious_classifier.pkl → Trained ML model
- nlp-model.py → Optional: Script to retrain the NLP model
- config.py → Centralized file paths for shared use between app and logger

# Libraries Used:
- Flask → Web server for dashboard
- sklearn + joblib → ML model training & loading
- pynput → Keylogger
- pyperclip → Clipboard monitoring
- Pillow (PIL) → Screenshot capture
- datetime, os, sys, threading → File handling, timing, multi-threading

# How to Run:
1. Install dependencies (Flask, scikit-learn, joblib, pynput, pyperclip, Pillow)
2. Run security.py → Starts the keylogger and detection
3. Run app/app.py → Starts the dashboard (visit localhost:5000)

# Note:
- For educational use only.
- Logs, screenshots, and alerts are saved inside /logs/ and /screens/ folders.

# For more info:
- See the full project report inside the GitHub repository.
