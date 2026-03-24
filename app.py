from flask import Flask, render_template, request
import random
import os

app = Flask(__name__)

history = []

@app.route("/")
def home():
    return render_template("index.html", history=history)

@app.route("/predict", methods=["POST"])
def predict():
    amount = float(request.form["amount"])
    location = request.form["location"]
    device = request.form["device"]
    time = request.form["time"]

    risk = 0

    if amount > 3000:
        risk += 40
    if location in ["Unknown", "Dubai"]:
        risk += 30
    if device == "New":
        risk += 20
    if time == "Night":
        risk += 10

    if risk >= 70:
        status = "High Risk ⚠"
        message = "🔐 OTP Verification Required"
    elif risk >= 40:
        status = "Medium Risk ⚠"
        message = "⚠ Suspicious Activity"
    else:
        status = "Low Risk ✅"
        message = "✅ Transaction Safe"

    history.append({
        "amount": amount,
        "location": location,
        "device": device,
        "time": time,
        "risk": risk,
        "status": status
    })

    return render_template("index.html",
                           prediction_text=status,
                           risk=risk,
                           message=message,
                           history=history)

@app.route("/simulate")
def simulate():
    amount = random.randint(100, 6000)
    location = random.choice(["India", "US", "UK", "Dubai", "Canada", "Unknown"])
    device = random.choice(["Mobile", "Laptop", "New"])
    time = random.choice(["Day", "Night"])

    risk = 0

    if amount > 3000:
        risk += 40
    if location in ["Unknown", "Dubai"]:
        risk += 30
    if device == "New":
        risk += 20
    if time == "Night":
        risk += 10

    if risk >= 70:
        status = "High Risk ⚠"
        message = "🔐 OTP Verification Required"
    elif risk >= 40:
        status = "Medium Risk ⚠"
        message = "⚠ Suspicious Activity"
    else:
        status = "Low Risk ✅"
        message = "✅ Transaction Safe"

    history.append({
        "amount": amount,
        "location": location,
        "device": device,
        "time": time,
        "risk": risk,
        "status": status
    })

    return render_template("index.html",
                           prediction_text=status,
                           risk=risk,
                           message=message,
                           history=history)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)