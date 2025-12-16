KGAT_b288e7fb4de6b808c258b6672b2d381c

export KAGGLE_API_TOKEN=KGAT_b288e7fb4de6b808c258b6672b2d381

💳 Credit Card Fraud Detection System

End-to-End Machine Learning Backend with Explainability

📌 Project Overview

This project presents an end-to-end Credit Card Fraud Detection System built using machine learning and a modern backend API.
The system is designed to detect fraudulent transactions by combining supervised classification models, unsupervised anomaly detection, and model explainability, all exposed through a FastAPI-based backend.

The solution follows real-world industry practices while remaining fully free, offline, and reproducible.

🎯 Objectives

Detect fraudulent credit card transactions with high accuracy

Serve machine learning models through a robust backend API

Support both single and batch transaction predictions

Combine multiple ML paradigms (supervised + unsupervised)

Provide explainable predictions for transparency

Maintain a clean, extensible, and production-style architecture

🧠 Machine Learning Approach
1. Supervised Learning Models

These models are trained using labeled transaction data (fraud / non-fraud):

LightGBM – Primary high-performance model

XGBoost – Ensemble-based gradient boosting model

Decision Tree – Interpretable baseline classifier

Each supervised model outputs a fraud probability score.

2. Unsupervised / Anomaly Detection Models

These models identify unusual transaction behavior without labels:

Isolation Forest – Detects anomalies based on isolation depth

KNN Anomaly Detection – Uses distance-based deviation

These models help capture previously unseen fraud patterns.

3. Hybrid Fraud Decision Logic

The final fraud decision is made by combining:

Supervised model probability

Isolation Forest anomaly flag

KNN anomaly distance

This hybrid approach improves robustness and reduces false negatives.

🔍 Explainability (XAI)

To ensure transparency and trust:

SHAP (SHapley Additive Explanations) is used

Applied to the LightGBM model

Returns the top contributing features influencing each prediction

This allows users to understand why a transaction was flagged as fraud.

📊 Dataset Description

Source: Kaggle – Credit Card Fraud Detection Dataset

Transactions are anonymized for privacy

Features:

V1 to V28: PCA-transformed components

Time: Time elapsed since first transaction

Amount: Transaction value

Class: Target variable (0 = Legitimate, 1 = Fraud)

The PCA transformation ensures privacy while preserving behavioral patterns.

🏗️ Project Architecture
fraud/
│
├── backend/
│   └── app.py              # FastAPI backend
│
├── training/
│   ├── train_lightgbm.py
│   ├── train_xgboost.py
│   ├── train_decision_tree.py
│   ├── train_isolation_forest.py
│   └── train_knn.py
│
├── models/
│   ├── fraud_lgbm.pkl
│   ├── fraud_xgb.pkl
│   ├── fraud_decision_tree.pkl
│   ├── fraud_isolation_forest.pkl
│   └── fraud_knn.pkl
│
├── data/
│   ├── raw/
│   │   └── creditcard.csv
│   └── schema.py
│
├── requirements.txt
└── README.md

🚀 Backend API Features
Available Endpoints
Endpoint	Description
/predict	Predict fraud for a single transaction
/predict/batch	Batch fraud prediction using CSV upload
/predict/hybrid	Hybrid decision using ML + anomalies
/predict/explain	Explain prediction using SHAP
/health	System health and model status
🔧 Technology Stack

Python 3.11+

FastAPI – Backend framework

Scikit-learn

LightGBM

XGBoost

SHAP

Pandas / NumPy

Joblib

All components are open-source and free.

▶️ How to Run the Project
1. Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

2. Install Dependencies
pip install -r requirements.txt

3. Train Models
python -m training.train_lightgbm
python -m training.train_xgboost
python -m training.train_decision_tree
python -m training.train_isolation_forest
python -m training.train_knn

4. Start Backend Server
uvicorn backend.app:app --reload

5. Open API Documentation
http://127.0.0.1:8000/docs

🧪 Example Output
{
  "model": "lightgbm",
  "fraud_probability": 0.0000000044,
  "is_fraud": false
}


Hybrid prediction:

{
  "fraud_probability": 0.63,
  "isolation_forest_anomaly": true,
  "knn_anomaly": false,
  "final_decision": true
}

📈 Learning Outcomes

Applied supervised and unsupervised learning

Built a production-style ML backend

Implemented hybrid fraud detection logic

Used explainable AI (XAI) techniques

Designed scalable API endpoints

Gained experience in real-world ML system design


✅ Conclusion

This project demonstrates a complete, end-to-end machine learning backend for fraud detection.
It combines accuracy, interpretability, and engineering best practices while remaining fully accessible and cost-free.
