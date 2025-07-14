import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

X = []
y = []

# Generate 1000 fake examples
for _ in range(1000):
    vibration = np.random.uniform(0.1, 3.5)
    temperature = np.random.uniform(25, 90)
    current = np.random.uniform(0.5, 15.0)

    fault = int(vibration > 2.5 or temperature > 70 or current > 12)

    X.append([vibration, temperature, current])
    y.append(fault)

# Split, train, test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
print("✅ Model accuracy:", accuracy_score(y_test, model.predict(X_test)))

# Save model
joblib.dump(model, "model.pkl")
