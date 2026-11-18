import streamlit as st
import pickle
import numpy as np
import plotly.graph_objects as go

# ── User Database ──
USERS = {
    "admin":   {"password": "admin123",  "role": "Admin",  "name": "Administrator"},
    "doctor":  {"password": "doctor123", "role": "Doctor", "name": "Dr. Smith"},
    "patient": {"password": "pass123",   "role": "Patient","name": "John Doe"},
}

st.set_page_config(
    page_title="Disease Prediction",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0d0d0d 0%, #1a0533 50%, #0d1a33 100%);
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0533 0%, #0d1a33 100%);
        border-right: 2px solid #ff6b6b;
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    h1 {
        background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
    }
    h2, h3 { color: #ffd93d !important; }
    .stNumberInput input, .stTextInput input {
        background-color: #1a1a2e !important;
        color: #ffffff !important;
        border: 1px solid #ff6b6b !important;
        border-radius: 10px !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #ff6b6b, #ffd93d) !important;
        color: #0d0d0d !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 40px !important;
        width: 100% !important;
        transition: transform 0.2s !important;
        box-shadow: 0 4px 20px rgba(255,107,107,0.4) !important;
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
    }
    .stSuccess {
        background: linear-gradient(90deg, #0d2b1a, #1a4731) !important;
        border-left: 5px solid #6bcb77 !important;
        border-radius: 10px !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    .stAlert { border-radius: 10px !important; font-size: 18px !important; }
    .page-banner {
        background: linear-gradient(90deg, #1a0533, #0d1a33);
        border-radius: 15px;
        padding: 20px 30px;
        margin-bottom: 20px;
        border-left: 5px solid #ffd93d;
    }
    .page-banner h2 { color: #ffd93d !important; margin: 0 !important; }
    .page-banner p  { color: #a0c4ff !important; margin: 5px 0 0 0 !important; }
    .login-box {
        background: linear-gradient(135deg, #1a0533, #0d1a33);
        border: 2px solid #ff6b6b;
        border-radius: 20px;
        padding: 40px;
        max-width: 450px;
        margin: 50px auto;
        box-shadow: 0 8px 32px rgba(255,107,107,0.2);
    }
    .user-badge {
        background: linear-gradient(90deg, #ff6b6b, #ffd93d);
        color: #0d0d0d;
        border-radius: 20px;
        padding: 5px 15px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 10px;
    }
    hr { border-color: #ff6b6b !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

# ── Login Page ──
def login_page():
    st.markdown("""
    <div style='text-align:center; padding: 20px 0;'>
        <h1>🏥 Disease Prediction System</h1>
        <p style='color:#a0c4ff; font-size:18px;'>AI Powered Medical Diagnosis</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='login-box'>
            <h2 style='text-align:center; color:#ffd93d !important;'>🔐 Login</h2>
            <p style='text-align:center; color:#a0c4ff;'>Please login to continue</p>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter password")

        if st.button("🚀 Login"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username  = username
                st.session_state.user_name = USERS[username]["name"]
                st.session_state.user_role = USERS[username]["role"]
                st.success(f"✅ Welcome {USERS[username]['name']}!")
                st.rerun()
            else:
                st.error("❌ Wrong username or password!")

        st.markdown("---")
        st.markdown("""
        <div style='text-align:center;'>
            <p style='color:#a0c4ff; font-size:13px;'>Demo Accounts:</p>
            <p style='color:#ffd93d; font-size:12px;'>
            👑 admin / admin123<br>
            👨‍⚕️ doctor / doctor123<br>
            👤 patient / pass123
            </p>
        </div>
        """, unsafe_allow_html=True)

# ── Main App ──
def main_app():
    # Load models
    diabetes_model = pickle.load(open('trained_model.pkl', 'rb'))
    heart_model    = pickle.load(open('heart_model.pkl', 'rb'))
    cancer_model   = pickle.load(open('cancer_model.pkl', 'rb'))

    # Helper: Gauge
    def show_gauge(probability, title):
        color = "#6bcb77" if probability < 40 else "#ffd93d" if probability < 70 else "#ff6b6b"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=probability,
            title={'text': title, 'font': {'size': 18, 'color': 'white'}},
            number={'font': {'color': color, 'size': 40}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': 'white'},
                'bar': {'color': color},
                'bgcolor': '#1a1a2e',
                'steps': [
                    {'range': [0,  40], 'color': '#0d2b1a'},
                    {'range': [40, 70], 'color': '#2b2000'},
                    {'range': [70,100], 'color': '#2b0d0d'}
                ],
            }
        ))
        fig.update_layout(
            height=280,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Helper: Comparison
    def show_comparison(labels, yours, normal, title):
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Normal", x=labels, y=normal, marker_color="#6bcb77"))
        fig.add_trace(go.Bar(name="Yours",  x=labels, y=yours,  marker_color="#ff6b6b"))
        fig.update_layout(
            title={'text': title, 'font': {'color': '#ffd93d'}},
            barmode='group', height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(13,13,13,0.8)',
            font={'color': 'white'},
            xaxis={'gridcolor': '#2d2d5e', 'color': 'white'},
            yaxis={'gridcolor': '#2d2d5e', 'color': 'white'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Sidebar
    st.sidebar.markdown("## 🏥 Disease Prediction")
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div class='user-badge'>
        👤 {st.session_state.user_name}
    </div>
    <p style='color:#a0c4ff; font-size:13px;'>
        Role: {st.session_state.user_role}
    </p>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    page = st.sidebar.radio("📋 Select Disease", [
        "🩸 Diabetes Prediction",
        "💓 Heart Disease Prediction",
        "🫁 Cancer Prediction"
    ])

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Model Accuracy")
    st.sidebar.success("🩸 Diabetes: 72.08%")
    st.sidebar.warning("💓 Heart: 98.54%")
    st.sidebar.info("🫁 Cancer: 96.49%")
    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username  = ""
        st.session_state.user_name = ""
        st.session_state.user_role = ""
        st.rerun()

    # ─── DIABETES ───
    if page == "🩸 Diabetes Prediction":
        st.markdown("""<div class='page-banner'>
            <h2>🩸 Diabetes Prediction System</h2>
            <p>Enter your health details to predict diabetes risk using AI</p>
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            pregnancies    = st.number_input("🤰 Pregnancies", 0, 20, 1)
            glucose        = st.number_input("🍬 Glucose Level", 0, 300, 120)
            blood_pressure = st.number_input("💉 Blood Pressure", 0, 150, 70)
            skin_thickness = st.number_input("📏 Skin Thickness", 0, 100, 20)
        with col2:
            insulin = st.number_input("💊 Insulin Level", 0, 900, 80)
            bmi     = st.number_input("⚖️ BMI", 0.0, 70.0, 25.0)
            dpf     = st.number_input("🧬 Diabetes Pedigree Function", 0.0, 3.0, 0.5)
            age     = st.number_input("🎂 Age", 1, 120, 25)
        st.write("")
        if st.button("🔍 Predict Diabetes Risk"):
            input_data  = np.array([[pregnancies, glucose, blood_pressure,
                                      skin_thickness, insulin, bmi, dpf, age]])
            prediction  = diabetes_model.predict(input_data)
            probability = diabetes_model.predict_proba(input_data)[0][1] * 100
            if prediction[0] == 1:
                st.error(f"⚠️ Diabetic Detected — Risk: {probability:.1f}%")
            else:
                st.success(f"✅ Non-Diabetic — Risk: {probability:.1f}%")
            st.markdown("---")
            st.subheader("📊 Health Analysis")
            col1, col2 = st.columns(2)
            with col1:
                show_gauge(probability, "Diabetes Risk %")
            with col2:
                show_comparison(
                    ["Glucose", "Blood Pressure", "BMI"],
                    [glucose, blood_pressure, bmi],
                    [85, 80, 22], "Your Values vs Normal"
                )

    # ─── HEART ───
    elif page == "💓 Heart Disease Prediction":
        st.markdown("""<div class='page-banner'>
            <h2>💓 Heart Disease Prediction System</h2>
            <p>Enter your cardiac details to predict heart disease risk using AI</p>
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            age      = st.number_input("🎂 Age", 1, 120, 50)
            sex      = st.selectbox("👤 Sex", [0,1], format_func=lambda x: "Female" if x==0 else "Male")
            cp       = st.number_input("💢 Chest Pain Type (0-3)", 0, 3, 0)
            trestbps = st.number_input("💉 Resting Blood Pressure", 80, 200, 120)
            chol     = st.number_input("🧪 Cholesterol", 100, 600, 200)
            fbs      = st.selectbox("🍬 Fasting Blood Sugar > 120", [0,1], format_func=lambda x: "No" if x==0 else "Yes")
            restecg  = st.number_input("📋 Resting ECG (0-2)", 0, 2, 0)
        with col2:
            thalach = st.number_input("❤️ Max Heart Rate", 60, 220, 150)
            exang   = st.selectbox("🏃 Exercise Induced Angina", [0,1], format_func=lambda x: "No" if x==0 else "Yes")
            oldpeak = st.number_input("📉 ST Depression", 0.0, 10.0, 1.0)
            slope   = st.number_input("📈 Slope (0-2)", 0, 2, 1)
            ca      = st.number_input("🫀 Major Vessels (0-4)", 0, 4, 0)
            thal    = st.number_input("🔬 Thal (0-3)", 0, 3, 2)
        st.write("")
        if st.button("🔍 Predict Heart Disease Risk"):
            input_data  = np.array([[age, sex, cp, trestbps, chol, fbs,
                                      restecg, thalach, exang, oldpeak,
                                      slope, ca, thal]])
            prediction  = heart_model.predict(input_data)
            probability = heart_model.predict_proba(input_data)[0][1] * 100
            if prediction[0] == 1:
                st.error(f"⚠️ Heart Disease Detected — Risk: {probability:.1f}%")
            else:
                st.success(f"✅ No Heart Disease — Risk: {probability:.1f}%")
            st.markdown("---")
            st.subheader("📊 Heart Health Analysis")
            col1, col2 = st.columns(2)
            with col1:
                show_gauge(probability, "Heart Disease Risk %")
            with col2:
                show_comparison(
                    ["Blood Pressure", "Cholesterol", "Max HR"],
                    [trestbps, chol, thalach],
                    [120, 200, 160], "Your Values vs Normal"
                )

    # ─── CANCER ───
    elif page == "🫁 Cancer Prediction":
        st.markdown("""<div class='page-banner'>
            <h2>🫁 Cancer Prediction System</h2>
            <p>Enter tumor details to detect breast cancer risk using AI</p>
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            radius_mean    = st.number_input("📐 Radius Mean", 0.0, 50.0, 14.0)
            texture_mean   = st.number_input("🔲 Texture Mean", 0.0, 50.0, 19.0)
            perimeter_mean = st.number_input("📏 Perimeter Mean", 0.0, 250.0, 92.0)
            area_mean      = st.number_input("📦 Area Mean", 0.0, 2500.0, 654.0)
            smoothness     = st.number_input("〰️ Smoothness Mean", 0.0, 0.5, 0.096)
        with col2:
            compactness    = st.number_input("🔵 Compactness Mean", 0.0, 1.0, 0.10)
            concavity      = st.number_input("🔴 Concavity Mean", 0.0, 1.0, 0.09)
            concave_points = st.number_input("📍 Concave Points Mean", 0.0, 1.0, 0.05)
            symmetry       = st.number_input("⚖️ Symmetry Mean", 0.0, 1.0, 0.18)
            fractal        = st.number_input("🔬 Fractal Dimension Mean", 0.0, 0.5, 0.06)
        st.write("")
        if st.button("🔍 Predict Cancer Risk"):
            input_data  = np.array([[radius_mean, texture_mean, perimeter_mean,
                                      area_mean, smoothness, compactness,
                                      concavity, concave_points, symmetry, fractal,
                                      0,0,0,0,0,0,0,0,0,0,
                                      0,0,0,0,0,0,0,0,0,0]])
            prediction  = cancer_model.predict(input_data)
            probability = cancer_model.predict_proba(input_data)[0][1] * 100
            if prediction[0] == 1:
                st.error(f"⚠️ Malignant Cancer Detected — Risk: {probability:.1f}%")
            else:
                st.success(f"✅ Benign - No Cancer — Risk: {probability:.1f}%")
            st.markdown("---")
            st.subheader("📊 Cancer Risk Analysis")
            col1, col2 = st.columns(2)
            with col1:
                show_gauge(probability, "Cancer Risk %")
            with col2:
                show_comparison(
                    ["Radius", "Texture", "Smoothness x100"],
                    [radius_mean, texture_mean, smoothness*100],
                    [12.0, 18.0, 9.6], "Your Values vs Normal"
                )

# ── Run App ──
if st.session_state.logged_in:
    main_app()
else:
    login_page()