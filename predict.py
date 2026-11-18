import pickle
import numpy as np

# Load trained model
with open('trained_model.pkl', 'rb') as f:
    model = pickle.load(f)

def predict_disease(pregnancies, glucose, blood_pressure,
                    skin_thickness, insulin, bmi, dpf, age):
    
    input_data = np.array([[pregnancies, glucose, blood_pressure,
                            skin_thickness, insulin, bmi, dpf, age]])
    
    prediction = model.predict(input_data)
    probability = model.predict_proba(input_data)[0][1] * 100
    
    if prediction[0] == 1:
        return f"⚠️ Diabetic (Risk: {probability:.1f}%)"
    else:
        return f"✅ Non-Diabetic (Risk: {probability:.1f}%)"