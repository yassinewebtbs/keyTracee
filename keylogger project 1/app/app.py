from flask import Flask, render_template
import os
import glob

app = Flask(__name__)

# code for path and directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ALERT_FILE = os.path.join(BASE_DIR, 'logs', 'alert_logs.txt')  # Updated path to match config.py
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'static', 'screens')


def parse_alerts():
    data = []
    suspicious_count = 0
    last_active = None
    suspicious_texts = []
    screenshots = []

    if not os.path.exists(ALERT_FILE):
        print(f"[ERROR] File not found: {ALERT_FILE}")
        return data, suspicious_texts, screenshots

    with open(ALERT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("[ALERT]"):
                try:
                    # timestamp 
                    parts = line.split("→")
                    timestamp_str = parts[0].replace("[ALERT]", "").strip()
                    
                    #  suspicious text
                    if len(parts) > 1:
                        suspicious_text = parts[1].strip()
                        # Remove confidence part 
                        if " (confidence:" in suspicious_text:
                            suspicious_text = suspicious_text.split(" (confidence:")[0].strip()
                        suspicious_texts.append({
                            "timestamp": timestamp_str,
                            "text": suspicious_text
                        })
                    
                    suspicious_count += 1
                    last_active = timestamp_str  
                except Exception as e:
                    print(f"[WARN] Failed to parse line: {line.strip()}\n{e}")

    # screenshots
    if os.path.exists(SCREENSHOT_DIR):
        screenshot_files = glob.glob(os.path.join(SCREENSHOT_DIR, "screenshot_*.png"))
        for file_path in screenshot_files:
            file_name = os.path.basename(file_path)
            screenshots.append({
                "path": file_name,
                "timestamp": file_name.replace("screenshot_", "").replace(".png", "").replace("_", " ")
            })

    if suspicious_count > 0:
        data.append({
            "name": "John Doe",  # static name for now
            "suspicious": suspicious_count,
            "last_active": last_active
        })

    return data, suspicious_texts, screenshots

@app.route('/')
def dashboard():
    employee_data, suspicious_texts, screenshots = parse_alerts()
    return render_template("index.html", 
                          employees=employee_data,
                          suspicious_texts=suspicious_texts,
                          screenshots=screenshots)

if __name__ == '__main__':
    app.run(debug=True)