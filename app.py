import os
import io
import base64
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from flask import Flask, render_template_string, request
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Load dataset and train ML model on startup
DATA_PATH = 'nutrition_deficiency_local_health_survey.csv'
df = pd.read_csv(DATA_PATH)

def train_model():
    data = df.copy()
    le_gender = LabelEncoder()
    le_area = LabelEncoder()
    le_diet = LabelEncoder()
    le_activity = LabelEncoder()
    le_target = LabelEncoder()
    
    data['Gender_Enc'] = le_gender.fit_transform(data['Gender'])
    data['Area_Enc'] = le_area.fit_transform(data['Area'])
    data['Diet_Enc'] = le_diet.fit_transform(data['Dietary_Pattern'])
    data['Activity_Enc'] = le_activity.fit_transform(data['Physical_Activity'])
    data['Target_Enc'] = le_target.fit_transform(data['Nutrition_Deficiency'])
    
    features = ['Age', 'BMI', 'Hemoglobin_g_dL', 'Iron_ug_dL', 'Vitamin_D_ng_mL', 
                'Vitamin_B12_pg_mL', 'Calcium_mg_dL', 'Gender_Enc', 'Area_Enc', 
                'Diet_Enc', 'Activity_Enc']
    
    X = data[features]
    y = data['Target_Enc']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model, le_gender, le_area, le_diet, le_activity, le_target, features

model, le_gender, le_area, le_diet, le_activity, le_target, feature_cols = train_model()

# Professional Multi-Tab HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nutrition Deficiency Analysis | Data Science Portal</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
        }
        .navbar {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .hero-section {
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
            color: white;
            padding: 35px 0;
            margin-bottom: 30px;
            border-radius: 0 0 20px 20px;
        }
        .nav-pills .nav-link {
            color: #475569;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        .nav-pills .nav-link.active {
            background-color: #2563eb;
            color: white;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
            background: #ffffff;
            transition: transform 0.2s ease;
        }
        .metric-card {
            border-left: 5px solid #2563eb;
        }
        .table-custom th {
            background-color: #f1f5f9;
            color: #334155;
            font-weight: 600;
        }
        footer {
            background: #0f172a;
            color: #94a3b8;
            padding: 25px 0;
            margin-top: 60px;
            text-align: center;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>

    <!-- Professional Navbar -->
    <nav class="navbar navbar-dark navbar-expand-lg px-4 py-3">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold fs-5" href="#">
                <i class="fa-solid fa-heart-pulse text-danger me-2"></i>NutriHealth Analytics Studio
            </a>
            <div class="d-flex align-items-center">
                <span class="badge bg-light text-dark px-3 py-2 fw-semibold">B.Sc. Data Science Mini Project</span>
            </div>
        </div>
    </nav>

    <!-- Hero Header -->
    <div class="hero-section text-center">
        <div class="container">
            <h1 class="fw-bold mb-2">Nutrition Deficiency Analysis Using Local Health Survey Data</h1>
            <p class="text-light opacity-8 mb-0">Advanced Exploratory Data Analysis, Multi-Sheet Insights & Machine Learning Diagnostics</p>
        </div>
    </div>

    <div class="container mb-5">
        
        <!-- Summary Metric Cards -->
        <div class="row g-4 mb-4">
            <div class="col-md-3">
                <div class="card metric-card p-3">
                    <div class="d-flex align-items-center">
                        <div class="bg-primary bg-opacity-10 p-3 rounded text-primary fs-3 me-3">
                            <i class="fa-solid fa-users"></i>
                        </div>
                        <div>
                            <span class="text-muted small fw-semibold text-uppercase">Total Records</span>
                            <h4 class="fw-bold mb-0 text-dark">{{ total_records }}</h4>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card p-3" style="border-left-color: #10b981;">
                    <div class="d-flex align-items-center">
                        <div class="bg-success bg-opacity-10 p-3 rounded text-success fs-3 me-3">
                            <i class="fa-solid fa-user-clock"></i>
                        </div>
                        <div>
                            <span class="text-muted small fw-semibold text-uppercase">Mean Age</span>
                            <h4 class="fw-bold mb-0 text-dark">{{ avg_age }} <span class="fs-6 text-muted">yrs</span></h4>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card p-3" style="border-left-color: #f59e0b;">
                    <div class="d-flex align-items-center">
                        <div class="bg-warning bg-opacity-10 p-3 rounded text-warning fs-3 me-3">
                            <i class="fa-solid fa-weight-scale"></i>
                        </div>
                        <div>
                            <span class="text-muted small fw-semibold text-uppercase">Mean BMI</span>
                            <h4 class="fw-bold mb-0 text-dark">{{ avg_bmi }} <span class="fs-6 text-muted">kg/m²</span></h4>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card p-3" style="border-left-color: #8b5cf6;">
                    <div class="d-flex align-items-center">
                        <div class="bg-purple bg-opacity-10 p-3 rounded text-purple fs-3 me-3" style="color: #8b5cf6;">
                            <i class="fa-solid fa-shield-heart"></i>
                        </div>
                        <div>
                            <span class="text-muted small fw-semibold text-uppercase">ML Accuracy</span>
                            <h4 class="fw-bold mb-0 text-dark">Random Forest</h4>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Navigation Tabs (Multi-View Sheets) -->
        <ul class="nav nav-pills mb-4 justify-content-center bg-white p-2 rounded shadow-sm" id="pills-tab" role="tablist">
            <li class="nav-item mx-1" role="presentation">
                <button class="nav-link {% if active_tab == 'overview' %}active{% endif %}" id="pills-overview-tab" data-bs-toggle="pill" data-bs-target="#pills-overview" type="button" role="tab"><i class="fa-solid fa-chart-pie me-2"></i>1. Overview & EDA Visuals</button>
            </li>
            <li class="nav-item mx-1" role="presentation">
                <button class="nav-link {% if active_tab == 'sheets' %}active{% endif %}" id="pills-sheets-tab" data-bs-toggle="pill" data-bs-target="#pills-sheets" type="button" role="tab"><i class="fa-solid fa-table-cells me-2"></i>2. Aggregated Sheets (Area & Diet)</button>
            </li>
            <li class="nav-item mx-1" role="presentation">
                <button class="nav-link {% if active_tab == 'predict' %}active{% endif %}" id="pills-predict-tab" data-bs-toggle="pill" data-bs-target="#pills-predict" type="button" role="tab"><i class="fa-solid fa-stethoscope me-2"></i>3. ML Diagnostic Predictor</button>
            </li>
            <li class="nav-item mx-1" role="presentation">
                <button class="nav-link {% if active_tab == 'raw' %}active{% endif %}" id="pills-raw-tab" data-bs-toggle="pill" data-bs-target="#pills-raw" type="button" role="tab"><i class="fa-solid fa-database me-2"></i>4. Raw Data Inspector</button>
            </li>
        </ul>

        <!-- Tab Contents -->
        <div class="tab-content" id="pills-tabContent">
            
            <!-- TAB 1: OVERVIEW & EDA -->
            <div class="tab-pane fade {% if active_tab == 'overview' %}show active{% endif %}" id="pills-overview" role="tabpanel">
                <div class="row g-4">
                    <div class="col-lg-6">
                        <div class="card p-4 h-100">
                            <h5 class="fw-bold text-dark mb-3"><i class="fa-solid fa-chart-bar text-primary me-2"></i>Distribution of Top Nutritional Deficiencies</h5>
                            <p class="text-muted small">Frequency count of primary reported nutritional conditions across surveyed participants.</p>
                            <div class="text-center mt-3">
                                <img src="data:image/png;base64,{{ plots.def_dist }}" class="img-fluid rounded border p-2 bg-light" alt="Deficiency Distribution">
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-6">
                        <div class="card p-4 h-100">
                            <h5 class="fw-bold text-dark mb-3"><i class="fa-solid fa-chart-scatter text-success me-2"></i>BMI vs Hemoglobin Correlation</h5>
                            <p class="text-muted small">Scatter analysis grouped by urban and rural geographical demographics.</p>
                            <div class="text-center mt-3">
                                <img src="data:image/png;base64,{{ plots.bmi_hemo }}" class="img-fluid rounded border p-2 bg-light" alt="BMI vs Hemoglobin">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: AGGREGATED SHEETS (AREA & DIET) -->
            <div class="tab-pane fade {% if active_tab == 'sheets' %}show active{% endif %}" id="pills-sheets" role="tabpanel">
                <div class="row g-4">
                    <!-- Sheet A: Area Analysis -->
                    <div class="col-lg-12">
                        <div class="card p-4 mb-4">
                            <h5 class="fw-bold text-dark mb-2"><i class="fa-solid fa-map-location-dot text-primary me-2"></i>Sheet View A: Health Metrics Aggregated by Geographic Area</h5>
                            <p class="text-muted small">Comparing mean BMI, Hemoglobin, Iron, and Vitamin D levels between Rural and Urban cohorts.</p>
                            <div class="table-responsive mt-3">
                                <table class="table table-hover table-custom align-middle text-center">
                                    <thead>
                                        <tr>
                                            <th>Area</th>
                                            <th>Participant Count</th>
                                            <th>Mean BMI (kg/m²)</th>
                                            <th>Mean Hemoglobin (g/dL)</th>
                                            <th>Mean Iron (µg/dL)</th>
                                            <th>Mean Vitamin D (ng/mL)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for idx, row in area_summary.iterrows() %}
                                        <tr>
                                            <td class="fw-bold text-dark"><i class="fa-solid fa-location-pin text-danger me-1"></i>{{ row['Area'] }}</td>
                                            <td><span class="badge bg-secondary">{{ row['Count'] }}</span></td>
                                            <td>{{ row['BMI'] }}</td>
                                            <td>{{ row['Hemoglobin_g_dL'] }}</td>
                                            <td>{{ row['Iron_ug_dL'] }}</td>
                                            <td>{{ row['Vitamin_D_ng_mL'] }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    <!-- Sheet B: Dietary Pattern Analysis -->
                    <div class="col-lg-12">
                        <div class="card p-4">
                            <h5 class="fw-bold text-dark mb-2"><i class="fa-solid fa-utensils text-success me-2"></i>Sheet View B: Health Metrics Aggregated by Dietary Pattern</h5>
                            <p class="text-muted small">Evaluating how dietary habits influence biological markers and nutrient distribution.</p>
                            <div class="table-responsive mt-3">
                                <table class="table table-hover table-custom align-middle text-center">
                                    <thead>
                                        <tr>
                                            <th>Dietary Pattern</th>
                                            <th>Participant Count</th>
                                            <th>Mean BMI (kg/m²)</th>
                                            <th>Mean Hemoglobin (g/dL)</th>
                                            <th>Mean Iron (µg/dL)</th>
                                            <th>Mean Vitamin D (ng/mL)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for idx, row in diet_summary.iterrows() %}
                                        <tr>
                                            <td class="fw-bold text-dark"><i class="fa-solid fa-bowl-food text-warning me-1"></i>{{ row['Dietary_Pattern'] }}</td>
                                            <td><span class="badge bg-secondary">{{ row['Count'] }}</span></td>
                                            <td>{{ row['BMI'] }}</td>
                                            <td>{{ row['Hemoglobin_g_dL'] }}</td>
                                            <td>{{ row['Iron_ug_dL'] }}</td>
                                            <td>{{ row['Vitamin_D_ng_mL'] }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 3: ML PREDICTOR -->
            <div class="tab-pane fade {% if active_tab == 'predict' %}show active{% endif %}" id="pills-predict" role="tabpanel">
                <div class="row justify-content-center">
                    <div class="col-lg-8">
                        <div class="card p-4 shadow-sm">
                            <h4 class="fw-bold text-primary mb-2 text-center"><i class="fa-solid fa-stethoscope me-2"></i>Machine Learning Diagnostic Predictor</h4>
                            <p class="text-muted text-center small mb-4">Provide patient biomarker values to predict likelihood of nutrition deficiency using our trained Random Forest model.</p>
                            
                            {% if prediction_result %}
                            <div class="alert alert-success border-0 shadow-sm text-center py-3 mb-4">
                                <span class="d-block small text-muted text-uppercase fw-bold">Inference Result</span>
                                <span class="fs-4 text-dark fw-bold"><i class="fa-solid fa-circle-check text-success me-2"></i>{{ prediction_result }}</span>
                            </div>
                            {% endif %}

                            <form method="POST" action="/predict_action" class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label small fw-bold text-secondary">Age</label>
                                    <input type="number" class="form-control" name="age" value="30" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label small fw-bold text-secondary">Gender</label>
                                    <select class="form-select" name="gender">
                                        {% for g in genders %}<option value="{{ g }}">{{ g }}</option>{% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label small fw-bold text-secondary">Area</label>
                                    <select class="form-select" name="area">
                                        {% for a in areas %}<option value="{{ a }}">{{ a }}</option>{% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label small fw-bold text-secondary">BMI (kg/m²)</label>
                                    <input type="number" step="0.1" class="form-control" name="bmi" value="21.5" required>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label small fw-bold text-secondary">Hemoglobin (g/dL)</label>
                                    <input type="number" step="0.1" class="form-control" name="hemoglobin" value="12.0" required>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label small fw-bold text-secondary">Iron (µg/dL)</label>
                                    <input type="number" step="0.1" class="form-control" name="iron" value="75.0" required>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label small fw-bold text-secondary">Vit D (ng/mL)</label>
                                    <input type="number" step="0.1" class="form-control" name="vit_d" value="24.0" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label small fw-bold text-secondary">Vit B12 (pg/mL)</label>
                                    <input type="number" step="0.1" class="form-control" name="vit_b12" value="350.0" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label small fw-bold text-secondary">Calcium (mg/dL)</label>
                                    <input type="number" step="0.1" class="form-control" name="calcium" value="8.9" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label small fw-bold text-secondary">Dietary Pattern</label>
                                    <select class="form-select" name="diet">
                                        {% for d in diets %}<option value="{{ d }}">{{ d }}</option>{% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label small fw-bold text-secondary">Physical Activity</label>
                                    <select class="form-select" name="activity">
                                        {% for act in activities %}<option value="{{ act }}">{{ act }}</option>{% endfor %}
                                    </select>
                                </div>
                                <div class="col-12 mt-4 text-center">
                                    <button type="submit" class="btn btn-primary btn-lg px-5 shadow">
                                        <i class="fa-solid fa-brain me-2"></i>Run Classification Inference
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 4: RAW DATA INSPECTOR -->
            <div class="tab-pane fade {% if active_tab == 'raw' %}show active{% endif %}" id="pills-raw" role="tabpanel">
                <div class="card p-4">
                    <h5 class="fw-bold text-dark mb-2"><i class="fa-solid fa-table text-warning me-2"></i>Raw Survey Dataset Inspector (First 50 Rows)</h5>
                    <p class="text-muted small">Direct view of underlying survey records loaded into the data science environment.</p>
                    <div class="table-responsive mt-3" style="max-height: 500px; overflow-y: auto;">
                        <table class="table table-striped table-hover table-custom align-middle small text-center">
                            <thead>
                                <tr>
                                    <th>Age</th><th>Gender</th><th>Area</th><th>BMI</th><th>Hemoglobin</th><th>Iron</th><th>Vit D</th><th>Vit B12</th><th>Calcium</th><th>Diet</th><th>Activity</th><th>Deficiency</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for idx, row in raw_sample.iterrows() %}
                                <tr>
                                    <td>{{ row['Age'] }}</td>
                                    <td>{{ row['Gender'] }}</td>
                                    <td>{{ row['Area'] }}</td>
                                    <td>{{ row['BMI'] }}</td>
                                    <td>{{ row['Hemoglobin_g_dL'] }}</td>
                                    <td>{{ row['Iron_ug_dL'] }}</td>
                                    <td>{{ row['Vitamin_D_ng_mL'] }}</td>
                                    <td>{{ row['Vitamin_B12_pg_mL'] }}</td>
                                    <td>{{ row['Calcium_mg_dL'] }}</td>
                                    <td>{{ row['Dietary_Pattern'] }}</td>
                                    <td>{{ row['Physical_Activity'] }}</td>
                                    <td class="fw-bold text-danger">{{ row['Nutrition_Deficiency'] }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <footer>
        <div class="container">
            <p class="mb-0">Nutrition Deficiency Analysis Studio &bull; B.Sc. Data Science Mini Project</p>
        </div>
    </footer>

    <!-- Bootstrap JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_page(active_tab='overview', prediction_result=None)

@app.route('/predict_action', methods=['POST'])
def predict_action():
    prediction_result = None
    try:
        age = float(request.form['age'])
        gender = request.form['gender']
        area = request.form['area']
        bmi = float(request.form['bmi'])
        hemoglobin = float(request.form['hemoglobin'])
        iron = float(request.form['iron'])
        vit_d = float(request.form['vit_d'])
        vit_b12 = float(request.form['vit_b12'])
        calcium = float(request.form['calcium'])
        diet = request.form['diet']
        activity = request.form['activity']
        
        g_enc = le_gender.transform([gender])[0]
        a_enc = le_area.transform([area])[0]
        d_enc = le_diet.transform([diet])[0]
        act_enc = le_activity.transform([activity])[0]
        
        input_data = pd.DataFrame([[
            age, bmi, hemoglobin, iron, vit_d, vit_b12, calcium,
            g_enc, a_enc, d_enc, act_enc
        ]], columns=feature_cols)
        
        pred_encoded = model.predict(input_data)[0]
        prediction_result = le_target.inverse_transform([pred_encoded])[0]
    except Exception as e:
        prediction_result = f"Error processing input: {str(e)}"

    return render_page(active_tab='predict', prediction_result=prediction_result)

def render_page(active_tab, prediction_result):
    total_records = len(df)
    avg_age = round(df['Age'].mean(), 1)
    avg_bmi = round(df['BMI'].mean(), 1)
    
    # Aggregated Summary Tables (Sheets) using standard pandas syntax
    area_summary = df.groupby('Area').agg({
        'Age': 'count',
        'BMI': lambda x: round(x.mean(), 2),
        'Hemoglobin_g_dL': lambda x: round(x.mean(), 2),
        'Iron_ug_dL': lambda x: round(x.mean(), 2),
        'Vitamin_D_ng_mL': lambda x: round(x.mean(), 2)
    }).rename(columns={'Age': 'Count'}).reset_index()

    diet_summary = df.groupby('Dietary_Pattern').agg({
        'Age': 'count',
        'BMI': lambda x: round(x.mean(), 2),
        'Hemoglobin_g_dL': lambda x: round(x.mean(), 2),
        'Iron_ug_dL': lambda x: round(x.mean(), 2),
        'Vitamin_D_ng_mL': lambda x: round(x.mean(), 2)
    }).rename(columns={'Age': 'Count'}).reset_index()

    raw_sample = df.head(50)
    
    plots = {}
    # Plot 1: Deficiency Distribution
    plt.figure(figsize=(7, 3.2))
    sns.countplot(y='Nutrition_Deficiency', data=df, order=df['Nutrition_Deficiency'].value_counts().index[:6], palette='crest')
    plt.title('Top Reported Deficiencies', fontsize=10, fontweight='bold', color='#1e293b')
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=150)
    img.seek(0)
    plots['def_dist'] = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    
    # Plot 2: Scatter plot
    plt.figure(figsize=(7, 3.2))
    sns.scatterplot(data=df, x='BMI', y='Hemoglobin_g_dL', hue='Area', palette='tab10', alpha=0.8, s=40)
    plt.title('BMI vs Hemoglobin by Area', fontsize=10, fontweight='bold', color='#1e293b')
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=150)
    img.seek(0)
    plots['bmi_hemo'] = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    return render_template_string(HTML_TEMPLATE,
                                   total_records=total_records,
                                   avg_age=avg_age,
                                   avg_bmi=avg_bmi,
                                   area_summary=area_summary,
                                   diet_summary=diet_summary,
                                   raw_sample=raw_sample,
                                   plots=plots,
                                   genders=le_gender.classes_,
                                   areas=le_area.classes_,
                                   diets=le_diet.classes_,
                                   activities=le_activity.classes_,
                                   active_tab=active_tab,
                                   prediction_result=prediction_result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)