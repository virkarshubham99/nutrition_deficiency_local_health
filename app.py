import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Page Configuration
st.set_page_config(
    page_title="Nutrition Deficiency Analysis",
    page_icon="🥗",
    layout="wide"
)

# Load Dataset
@st.cache_data
def load_data():
    return pd.read_csv('nutrition_deficiency_local_health_survey.csv')

df = load_data()

# Train ML Model
@st.cache_resource
def train_model(data):
    df_model = data.copy()
    le_gender = LabelEncoder()
    le_area = LabelEncoder()
    le_diet = LabelEncoder()
    le_activity = LabelEncoder()
    le_target = LabelEncoder()
    
    df_model['Gender_Enc'] = le_gender.fit_transform(df_model['Gender'])
    df_model['Area_Enc'] = le_area.fit_transform(df_model['Area'])
    df_model['Diet_Enc'] = le_diet.fit_transform(df_model['Dietary_Pattern'])
    df_model['Activity_Enc'] = le_activity.fit_transform(df_model['Physical_Activity'])
    df_model['Target_Enc'] = le_target.fit_transform(df_model['Nutrition_Deficiency'])
    
    features = ['Age', 'BMI', 'Hemoglobin_g_dL', 'Iron_ug_dL', 'Vitamin_D_ng_mL', 
                'Vitamin_B12_pg_mL', 'Calcium_mg_dL', 'Gender_Enc', 'Area_Enc', 
                'Diet_Enc', 'Activity_Enc']
    
    X = df_model[features]
    y = df_model['Target_Enc']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model, le_gender, le_area, le_diet, le_activity, le_target, features

model, le_gender, le_area, le_diet, le_activity, le_target, feature_cols = train_model(df)

# App Title & Header
st.title("🥗 Nutrition Deficiency Analysis Using Local Health Survey Data")
st.markdown("**B.Sc. Data Science Mini Project** — Exploratory Data Analysis, Multi-Sheet Insights & Machine Learning Diagnostics")
st.markdown("---")

# Top Metric Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Surveyed Records", len(df))
col2.metric("Average Cohort Age", f"{df['Age'].mean():.1f} yrs")
col3.metric("Average Cohort BMI", f"{df['BMI'].mean():.1f} kg/m²")
col4.metric("ML Model", "Random Forest")

st.markdown("")

# Multi-Tab Views (Sheets)
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. Overview & EDA Visuals", 
    "📋 2. Aggregated Sheets (Area & Diet)", 
    "🩺 3. ML Diagnostic Predictor", 
    "📂 4. Raw Data Inspector"
])

# TAB 1: Overview & EDA Visuals
with tab1:
    st.subheader("Exploratory Data Analysis (EDA)")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**Distribution of Top Nutritional Deficiencies**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.countplot(y='Nutrition_Deficiency', data=df, order=df['Nutrition_Deficiency'].value_counts().index[:6], palette='crest', ax=ax)
        ax.set_ylabel("")
        ax.set_xlabel("Count")
        st.pyplot(fig)
        
    with c2:
        st.markdown("**BMI vs Hemoglobin Correlation by Area**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(data=df, x='BMI', y='Hemoglobin_g_dL', hue='Area', palette='tab10', alpha=0.8, ax=ax)
        st.pyplot(fig)

# TAB 2: Aggregated Sheets
with tab2:
    st.subheader("Aggregated Health Survey Sheets")
    
    st.markdown("##### 📍 Sheet A: Aggregation by Geographic Area")
    area_summary = df.groupby('Area').agg(
        Count=('Age', 'count'),
        Mean_BMI=('BMI', lambda x: round(x.mean(), 2)),
        Mean_Hemoglobin=('Hemoglobin_g_dL', lambda x: round(x.mean(), 2)),
        Mean_Iron=('Iron_ug_dL', lambda x: round(x.mean(), 2)),
        Mean_Vitamin_D=('Vitamin_D_ng_mL', lambda x: round(x.mean(), 2))
    ).reset_index()
    st.dataframe(area_summary, use_container_width=True)
    
    st.markdown("##### 🍲 Sheet B: Aggregation by Dietary Pattern")
    diet_summary = df.groupby('Dietary_Pattern').agg(
        Count=('Age', 'count'),
        Mean_BMI=('BMI', lambda x: round(x.mean(), 2)),
        Mean_Hemoglobin=('Hemoglobin_g_dL', lambda x: round(x.mean(), 2)),
        Mean_Iron=('Iron_ug_dL', lambda x: round(x.mean(), 2)),
        Mean_Vitamin_D=('Vitamin_D_ng_mL', lambda x: round(x.mean(), 2))
    ).reset_index()
    st.dataframe(diet_summary, use_container_width=True)

# TAB 3: ML Diagnostic Predictor
with tab3:
    st.subheader("Machine Learning Diagnostic Predictor")
    st.markdown("Enter patient parameters to infer deficiency risk using the Random Forest model.")
    
    with st.form("prediction_form"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            gender = st.selectbox("Gender", le_gender.classes_)
            area = st.selectbox("Area", le_area.classes_)
            bmi = st.number_input("BMI (kg/m²)", min_value=10.0, max_value=50.0, value=21.5)
        with col_b:
            hemoglobin = st.number_input("Hemoglobin (g/dL)", min_value=5.0, max_value=20.0, value=12.0)
            iron = st.number_input("Iron (µg/dL)", min_value=5.0, max_value=200.0, value=75.0)
            vit_d = st.number_input("Vitamin D (ng/mL)", min_value=1.0, max_value=100.0, value=24.0)
        with col_c:
            vit_b12 = st.number_input("Vitamin B12 (pg/mL)", min_value=50.0, max_value=1000.0, value=350.0)
            calcium = st.number_input("Calcium (mg/dL)", min_value=4.0, max_value=15.0, value=8.9)
            diet = st.selectbox("Dietary Pattern", le_diet.classes_)
            activity = st.selectbox("Physical Activity", le_activity.classes_)
            
        submitted = st.form_submit_button("Run Classification Inference")
        
        if submitted:
            g_enc = le_gender.transform([gender])[0]
            a_enc = le_area.transform([area])[0]
            d_enc = le_diet.transform([diet])[0]
            act_enc = le_activity.transform([activity])[0]
            
            input_df = pd.DataFrame([[
                age, bmi, hemoglobin, iron, vit_d, vit_b12, calcium,
                g_enc, a_enc, d_enc, act_enc
            ]], columns=feature_cols)
            
            pred_enc = model.predict(input_df)[0]
            result = le_target.inverse_transform([pred_enc])[0]
            
            st.success(f"**Diagnostic Prediction Result:** {result}")

# TAB 4: Raw Data Inspector
with tab4:
    st.subheader("Raw Survey Dataset Inspector")
    st.dataframe(df, use_container_width=True)
