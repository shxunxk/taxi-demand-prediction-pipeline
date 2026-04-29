# 🚖 Ride Demand Forecasting MLOps Pipeline

## 📌 Overview

This project is an end-to-end **Machine Learning + MLOps system** that predicts ride demand across different city locations and time periods using NYC Taxi trip data.

The system simulates a real-world **urban mobility forecasting pipeline**, where new data arrives continuously and models must adapt using retraining strategies.

---

## 🎯 Problem Statement

Predict ride demand for each location and time bucket using historical trip data.  
The goal is to help optimize:

- Driver allocation  
- Ride pricing strategies  
- Urban traffic planning  

---

## 🧠 Approach

This project uses a **time-series based machine learning pipeline** with engineered features to capture temporal and spatial patterns.

### 🔹 Key Features Engineered

- Lag features (lag_1, lag_2, lag_7)
- Rolling statistics (mean, std)
- Time features (day of week, time bucket)
- Location-based demand patterns
- Passenger and trip distance aggregates

---

## ⚙️ Pipeline Steps

### 1. Data Ingestion
NYC Taxi trip data is loaded and cleaned from raw parquet files.

### 2. Aggregation
Data is grouped by:
- Pickup Location
- Date
- Time Bucket

Target variable:
- **Demand = number of trips per group**

---

### 3. Feature Engineering

- Temporal features (day, weekday)
- Lag features to capture past demand
- Rolling statistics for trend detection
- Encoding of time buckets and location patterns

---

### 4. Model Training

Models used:
- Gradient Boosting Regressor / XGBoost / LightGBM (optional)

Evaluation metric:
- Mean Absolute Error (MAE)

---

### 5. MLOps Component

- Reproducible pipeline
- Train/test time-series split
- Ready for CI/CD integration using GitHub Actions
- Modular structure for retraining

---

## 📊 Results

- Baseline MAE: ~33
- After feature engineering: ~15–19 MAE
- Best observed MAE: ~15.2

---

## 🏗️ Tech Stack

- Python
- Pandas, NumPy
- Scikit-learn
- XGBoost / LightGBM
- GitHub Actions (MLOps)
- Jupyter Notebook

---

## 🔄 Future Improvements

- Add weather + holiday data
- Deploy model using FastAPI
- Add real-time streaming ingestion
- Model monitoring & drift detection
- Dockerize full pipeline

---

## 🚀 Goal of this Project

To demonstrate a **production-style machine learning system** that goes beyond modeling and includes:

- Feature engineering at scale  
- Time-series modeling  
- Reproducible pipelines  
- MLOps readiness  

---

## 👨‍💻 Author

Built as a hands-on MLOps + Data Science project for real-world deployment readiness.
