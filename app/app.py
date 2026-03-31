from flask import Flask, render_template, request
import sqlite3
import pytesseract
import re
import cv2
import os
import uuid
import difflib

# Tesseract ka path verify kar lein
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__, template_folder='templates')

# ---------- DB ----------
def init_db():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper function for Fuzzy Matching (Smart Detection)
def is_similar(target, text_block, threshold=0.85):
    """
    Checks if a target string closely matches any word in the text block.
    Helps bypass common OCR mistakes (e.g., '0' vs 'O', '8' vs 'B').
    """
    words = text_block.split()
    for word in words:
        # Calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, target, word).ratio()
        if similarity >= threshold:
            return True
    return False

# ---------- HOME ----------
@app.route('/')
def home():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    data = c.execute("SELECT * FROM transactions").fetchall()

    total = len(data)
    fraud = sum(1 for d in data if d[2] == "FRAUD")
    genuine = total - fraud

    conn.close()

    return render_template('index.html',
                           data=data,
                           total=total,
                           fraud=fraud,
                           genuine=genuine)

# ---------- VERIFY ----------
@app.route('/verify', methods=['POST'])
def verify():
    txn_id = request.form.get('txn_id', '').strip()
    file = request.files.get('file')

    if not file or not txn_id:
        return "Missing Transaction ID or Image File", 400

    # Secure unique filename to prevent overwrite bugs
    filename = str(uuid.uuid4()) + ".png"
    filepath = os.path.join("temp", filename)
    
    # Ensure temp directory exists
    os.makedirs("temp", exist_ok=True)
    file.save(filepath)

    try:
        # ---------- IMPROVED OCR PREPROCESSING ----------
        img = cv2.imread(filepath)
        # Resize image to improve OCR readability for small text
        img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian Blur and Otsu's thresholding (Better than hardcoded 150)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        text = pytesseract.image_to_string(thresh)
        clean_text = text.lower()

        # ---------- SMART ID MATCH ----------
        # Uses standard 'in' check OR fuzzy logic for OCR typos
        clean_txn_id = txn_id.lower()
        id_match = (clean_txn_id in clean_text) or is_similar(clean_txn_id, clean_text)
        match_status = "ID matches screenshot ✅" if id_match else "ID mismatch ❌"

        # ---------- FINAL AMOUNT DETECTION ----------
        amount = "Not Found"

        # 1. Standard Indian Rupee format
        match = re.search(r'(?:rs\.?|inr|₹)\s*([\d,]+\.?\d*)', clean_text)
        if match:
            amount = match.group(1).replace(",", "")
        
        # 2. Context-based keywords
        if amount == "Not Found":
            match = re.search(r'(paid|debited|sent|amount)[^\d]{0,10}([\d,]+\.?\d*)', clean_text)
            if match:
                amount = match.group(2).replace(",", "")

        # 3. Fallback: Find largest valid number string (under 7 digits to avoid IDs)
        if amount == "Not Found":
            numbers = re.findall(r'\b[\d,]{2,}\b', clean_text)
            valid = [n.replace(",", "") for n in numbers if len(n.replace(",", "")) <= 6 and not n.startswith('0')]
            if valid:
                amount = valid[0] # Takes the first logical amount found

        # ---------- TIME EXTRACT ----------
        time = "Not Found"
        match = re.search(r'\d{1,2}:\d{2}\s?(?:am|pm|hrs)?', clean_text)
        if match:
            time = match.group()

        # ---------- FEATURES EXTRACT ----------
        has_upi = any(k in clean_text for k in ["upi", "gpay", "paytm", "phonepe", "bharatpe"])
        has_success = any(k in clean_text for k in ["success", "successful", "completed", "credited", "debited", "paid"])
        has_amount = amount != "Not Found"
        has_txn = any(k in clean_text for k in ["txn", "transaction", "utr", "ref", "reference"])

        # ---------- ADVANCED SCORING & CONFIDENCE ----------
        score_points = 0
        max_points = 100

        reasons = []

        # Weightage distribution (ML-like feature importance heuristic)
        if id_match: 
            score_points += 40
        else:
            reasons.append("Transaction ID mismatch or not found")
            
        if has_success: 
            score_points += 20
        else:
            reasons.append("No 'Success' or confirmation keyword detected")
            
        if has_upi or has_txn: 
            score_points += 20
        else:
            reasons.append("No UPI/Bank terminology detected")
            
        if has_amount: 
            score_points += 20
        else:
            reasons.append("Could not confidently detect payment amount")

        confidence = score_points

        # ---------- RESULT CLASSIFICATION ----------
        if confidence >= 80 and id_match:
            final_result = "GENUINE"
        elif 50 <= confidence < 80:
            final_result = "SUSPICIOUS"
        else:
            final_result = "FRAUD"

        # ---------- DB SAVE ----------
        conn = sqlite3.connect('transactions.db')
        c = conn.cursor()
        c.execute("INSERT INTO transactions (amount, status) VALUES (?, ?)", (amount, final_result))
        conn.commit()

        data = c.execute("SELECT * FROM transactions").fetchall()
        conn.close()

        total = len(data)
        fraud = sum(1 for d in data if d[2] == "FRAUD")
        genuine = total - fraud

        return render_template(
            'index.html',
            verify_result=True,
            txn_id=txn_id,
            match_status=match_status,
            final_result=final_result,
            confidence=confidence,
            amount=amount,
            time=time,
            extracted_text=text,
            reasons=reasons,
            total=total,
            fraud=fraud,
            genuine=genuine,
            data=data
        )

    finally:
        # CLEANUP: Always delete the temporary file after processing to save space
        if os.path.exists(filepath):
            os.remove(filepath)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)