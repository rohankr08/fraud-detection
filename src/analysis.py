import pandas as pd

print("=== FRAUD DETECTION PROJECT START ===\n")

df = pd.read_csv('data/creditcard.csv')

print("First 5 rows of dataset:\n")
print(df.head())

print("\nDataset shape:", df.shape)

print("\n--- Fraud vs Genuine Count ---\n")

counts = df['Class'].value_counts()
print(counts)

print("\n--- Percentage ---\n")

fraud = counts[1]
genuine = counts[0]

total = fraud + genuine

fraud_percent = (fraud / total) * 100
genuine_percent = (genuine / total) * 100

print(f"Fraud %: {fraud_percent:.4f}")
print(f"Genuine %: {genuine_percent:.4f}")

print("\n=== ANALYSIS COMPLETE ===")


print("\n=== STEP 3: DATA PREPROCESSING ===\n")

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

X = df.drop('Class', axis=1)
y = df['Class']

print("Features shape:", X.shape)
print("Target shape:", y.shape)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("\nTrain data:", X_train.shape)
print("Test data:", X_test.shape)

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

print("\nData scaling done successfully!")

print("\n=== STEP 3 COMPLETE ===")

print("\n=== STEP 4: MODEL TRAINING ===\n")

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

print("Model training complete!")

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("\nAccuracy:", accuracy)

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

print("\n=== STEP 4 COMPLETE ===")

print("\n=== STEP 5: IMPROVED MODEL ===\n")

from sklearn.ensemble import RandomForestClassifier

rf_model = RandomForestClassifier(
    n_estimators=20,
    class_weight='balanced',
    random_state=42
)

rf_model.fit(X_train, y_train)

print("Random Forest model trained!")

y_pred_rf = rf_model.predict(X_test)

accuracy_rf = accuracy_score(y_test, y_pred_rf)

print("\nAccuracy:", accuracy_rf)

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred_rf))

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred_rf))

print("\n=== STEP 5 COMPLETE ===")

print("\n=== STEP 6: ANOMALY DETECTION ===\n")

from sklearn.ensemble import IsolationForest

iso_model = IsolationForest(
    n_estimators=100,
    contamination=0.0017,  
    random_state=42
)

iso_model.fit(X_train)

print("Isolation Forest trained!")

y_pred_iso = iso_model.predict(X_test)

y_pred_iso = [1 if x == -1 else 0 for x in y_pred_iso]

accuracy_iso = accuracy_score(y_test, y_pred_iso)

print("\nAccuracy:", accuracy_iso)

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred_iso))

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred_iso))

print("\n=== STEP 6 COMPLETE ===")

print("\n=== STEP 7: HYBRID MODEL ===\n")


hybrid_pred = []

for i in range(len(y_pred_rf)):
    
    if y_pred_rf[i] == 1 or y_pred_iso[i] == 1:
        hybrid_pred.append(1)
    else:
        hybrid_pred.append(0)

accuracy_hybrid = accuracy_score(y_test, hybrid_pred)

print("\nHybrid Model Accuracy:", accuracy_hybrid)

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, hybrid_pred))

print("\nClassification Report:\n")
print(classification_report(y_test, hybrid_pred))

print("\n=== STEP 7 COMPLETE ===")

import joblib

joblib.dump(rf_model, 'models/fraud_model.pkl')

print("\nModel saved successfully!")
