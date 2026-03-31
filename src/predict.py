import joblib
import numpy as np

model = joblib.load('models/fraud_model.pkl')

print("=== Fraud Detection System ===\n")

amount = float(input("Enter transaction amount: "))
time = float(input("Enter transaction time (0-24): "))

features = np.zeros(30)

features[-1] = amount

is_high_amount = 1 if amount > 20000 else 0
is_night = 1 if time >= 0 and time <= 5 else 0

features[0] = is_high_amount
features[1] = is_night

features = features.reshape(1, -1)

prediction = model.predict(features)

print("\n=== RESULT ===")

if prediction[0] == 1:
    print("❌ Fraud Transaction Detected!")
else:
    print("✅ Genuine Transaction")

print("\nReason:")

if is_high_amount:
    print("- High transaction amount")

if is_night:
    print("- Transaction at unusual time")

if not is_high_amount and not is_night:
    print("- Normal transaction")