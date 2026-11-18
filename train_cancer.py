import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import pickle

# Load dataset
df = pd.read_csv('cancer.csv')

# Drop unnecessary columns
df = df.drop(['id', 'Unnamed: 32'], axis=1, errors='ignore')

# Encode diagnosis: M=1 (Malignant), B=0 (Benign)
le = LabelEncoder()
df['diagnosis'] = le.fit_transform(df['diagnosis'])

# Features & Target
X = df.drop('diagnosis', axis=1)
y = df['diagnosis']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Cancer Model Accuracy: {accuracy * 100:.2f}%")

# Save model
with open('cancer_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Cancer model saved as cancer_model.pkl")