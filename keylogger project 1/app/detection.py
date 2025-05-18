
import joblib
import re
from datetime import datetime
import os
import traceback

# script location
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the trained model
model_path = os.path.join(script_dir, "suspicious_classifier.pkl")
try:
    model = joblib.load(model_path)
    print(f"Model loaded successfully from {model_path}")
except Exception as e:
    print(f"Error loading model: {e}")
    print(f"Looking for model at: {model_path}")
    print("Please make sure to run improved_nlp_model.py first to create the model file.")
    raise

# Clean text:
def clean_text(text):
    #standardize input
    text = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} →", "", text)  # remove timestamps
    text = re.sub(r"\[.*?\]", "", text)  # remove [ENTER], etc.
    return text.strip().lower()

# Predict if sentence is suspicious
def check_sentence(text):
    cleaned = clean_text(text)
    if not cleaned:
        return False
    
    try:
        #prediction probabilities
        proba = model.predict_proba([cleaned])[0]
        
        # index of suspicious class
        suspicious_idx = list(model.classes_).index('suspicious')
        
        # confidence level 
        suspicious_confidence = proba[suspicious_idx]
        
        #  0.5 threshold for better detection
        is_suspicious = suspicious_confidence > 0.5
        
        if is_suspicious:
            # probability 
            print(f"Suspicious activity detected: '{cleaned}' (confidence: {suspicious_confidence*100:.1f}%)")
        
        return is_suspicious
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        traceback.print_exc()  # full traceback 
        return False

#  log the alert 
def log_alert(activity):
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alert_logs.txt")
    try:
        #  confidence score 
        cleaned = clean_text(activity)
        proba = model.predict_proba([cleaned])[0]
        suspicious_idx = list(model.classes_).index('suspicious')
        confidence = proba[suspicious_idx] * 100
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[ALERT] {datetime.now()} → {activity} (confidence: {confidence:.1f}%)\n")
            print(f"Alert logged: {activity} (confidence: {confidence:.1f}%)")
    except Exception as e:
        print(f"Error logging alert: {e}")
        # simple logging 
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[ALERT] {datetime.now()} → {activity}\n")

#  why a text was flaggeds
def explain_detection(text):
    cleaned = clean_text(text)
    if not cleaned:
        return "Empty text provided."
    
    try:
        # TF-IDF vectorizer 
        vectorizer = model.named_steps['tfidf']
        
        #feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Transform the text uwithh TF-IDF
        X_tfidf = vectorizer.transform([cleaned])
        
        # feature indices and values
        feature_indices = X_tfidf.nonzero()[1]
        tfidf_scores = [X_tfidf[0, idx] for idx in feature_indices]
        
        #  feature names and scores
        feature_values = [(feature_names[idx], tfidf_scores[i]) for i, idx in enumerate(feature_indices)]
        
        # Sort by scores 
        sorted_features = sorted(feature_values, key=lambda x: x[1], reverse=True)
        
        #  top features
        top_features = sorted_features[:5]
        
        # explanation
        explanation = "This text was flagged because it contains concerning terms:\n"
        for term, score in top_features:
            explanation += f"- '{term}' (importance: {score:.4f})\n"
        
        return explanation
    
    except Exception as e:
        return f"Could not explain detection due to error: {e}"

# For testing 
if __name__ == "__main__":
    test_sentences = [
        "I went to school today",
        "My password is admin123",
        "Let's bypass the security system",
        "Can you help me with this report?",
        "I'm sending my bank account details",
        "Password: 123456",
        "username and password for the system",
        "accessing sensitive files"
    ]
    
    print("Testing detection module:")
    for sentence in test_sentences:
        is_suspicious = check_sentence(sentence)
        result = "SUSPICIOUS" if is_suspicious else "NORMAL"
        print(f"'{sentence}' -> {result}")
        
        if is_suspicious:
            print(explain_detection(sentence))
        print()