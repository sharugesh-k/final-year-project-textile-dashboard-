# PROJECT VIVA PRESENTATION
# Textile Mill Intelligent Monitoring System

---

## SLIDE 1: TITLE SLIDE
**Project Title:** Textile Mill Intelligent Monitoring System
**Student Name:** [Your Name Here]
**Department:** Computer Science & Engineering
**College:** [Your College Name]
**Guide Name:** [Professor’s Name]
**Academic Year:** 2025-2026

---

## SLIDE 2: ABSTRACT
*   **Problem:** Textile mills suffer from unexplained downtime and supply chain delays.
*   **Solution:** Developed a real-time monitoring system using IoT-simulated data and Machine Learning.
*   **Outcome:** Provides live production insights, predicts machine failures, and forecasts supplier delays.
*   **Key Tech:** Python, Streamlit, Supabase (SQL), Scikit-Learn.

---

## SLIDE 3: INTRODUCTION
*   **Background:** The textile industry is capital-intensive with high machinery costs.
*   **Relevance:** Small inefficiencies lead to massive financial losses.
*   **Need:** Transition from "Reactive Maintenance" to "Predictive Intelligence" (Industry 4.0).
*   **Goal:** Digitize the factory floor to enable data-driven decision-making.

---

## SLIDE 4: PROBLEM STATEMENT
*   **Lack of Visibility:** Managers cannot see real-time machine status or efficiency.
*   **Unplanned Downtime:** Machines fail unexpectedly, halting the entire production line.
*   **Supply Chain Blind Spots:** No early warning for raw material delays.
*   **Static Reporting:** Existing tools only show "what happened," not "what will happen."

---

## SLIDE 5: OBJECTIVES
*   **Primary Objective:** To build a centralized dashboard for monitoring real-time textile production metrics.
*   **Secondary Objectives:**
    *   Predict production risks using Machine Learning.
    *   Forecast supplier delivery delays.
    *   Visualize efficiency trends to identify bottlenecks.

---

## SLIDE 6: SYSTEM OVERVIEW
*   **Data Source:** Synthetic data generator simulating IoT sensors and supplier logs.
*   **Database:** Supabase (Cloud PostgreSQL) for persistent storage.
*   **Intelligence:** Scikit-learn models for predictive analytics.
*   **Interface:** Streamlit-based web dashboard for interactions.

---

## SLIDE 7: SYSTEM ARCHITECTURE
*(Diagram Description: Data Source → Ingestion → Storage → ML Engine → UI)*
*   **Data Generation Layer:** Simulates Machine (Speed, Temp) and Supplier data.
*   **Storage Layer:** Supabase stores raw logs and historical records.
*   **Processing Layer:** Python scripts fetch, clean, and prepare features.
*   **ML & Application Layer:** Inference engine runs models; Streamlit renders the UI.

---

## SLIDE 8: DATA FLOW DIAGRAM (DFD)
*   **Level 0 (Context):** User interacts with the System; System queries Database and ML Models.
*   **Level 1 (Process Detail):**
    1.  `simulate_all.py` generates data → Pushes to `Supabase`.
    2.  `dashboard.py` fetches live data.
    3.  `model_inference.py` processes features & predicts risks.
    4.  Result displayed on Dashboard.

---

## SLIDE 9: DATABASE DESIGN
*   **Database:** PostgreSQL (via Supabase).
*   **Table 1: `production_data`**
    *   Cols: `machine_id`, `speed_rpm`, `temperature_c`, `actual_output`, `timestamp`.
    *   Purpose: Tracks shop floor performance.
*   **Table 2: `supplier_data`**
    *   Cols: `supplier_id`, `order_quantity`, `expected_date`, `actual_date`, `status`.
    *   Purpose: Tracks raw material logistics.

---

## SLIDE 10: DATA COLLECTION & PREPROCESSING
*   **Source:** Python-based simulation with causal logic (e.g., High Temp → Low Efficiency).
*   **Preprocessing:**
    *   **Handling Missing Values:** Imputation with rolling averages.
    *   **Feature Engineering:** Created `Thermal_Stress_Index` and `Load_Factor`.
    *   **Normalization:** Scaled RPM and Temperature for model consistency.

---

## SLIDE 11: MACHINE LEARNING MODELS USED
*   **Production Risk:** Random Forest Classifier.
    *   *Why:* Handles non-linear relationships and categorical data well.
*   **Supplier Delay:** Random Forest Classifier.
    *   *Why:* Robust against noise and outliers in logistics data.
*   **Efficiency Prediction:** Linear Regression.
    *   *Why:* Provides interpretable coefficients for efficiency factors.

---

## SLIDE 12: MODEL 1: PRODUCTION RISK PREDICTION
*   **Algorithm:** Random Forest Classifier.
*   **Inputs:** `speed_rpm`, `temperature_c`, `downtime_minutes`, `target_output`.
*   **Derived Feature:** `Thermal_Stress` (measures heat impact at high speeds).
*   **Output:** Risk Level (Low / Medium / High / Critical).

---

## SLIDE 13: MODEL 2: SUPPLIER DELAY PREDICTION
*   **Algorithm:** Random Forest Classifier.
*   **Inputs:** `supplier_id`, `transportation_status`, `distance_km`, `material_type`.
*   **Output:** Probability of delay (> 50% indicates risk).
*   **Impact:** Allows managers to reschedule production before materials run out.

---

## SLIDE 14: MODEL 3: EFFICIENCY PREDICTION
*   **Algorithm:** Linear Regression.
*   **Inputs:** `downtime_minutes`, `speed_rpm`, `temperature_c`.
*   **Output:** Predicted Efficiency % (0-100).
*   **Suitability:** Simple and effective for spotting basic trends (e.g., +Downtime = -Efficiency).

---

## SLIDE 15: MODEL TRAINING & TESTING
*   **Dataset:** Historical aggregated logs (10,000+ records).
*   **Split:** 80% Training, 20% Testing.
*   **Validation:** K-Fold Cross Validation.
*   **Metrics:**
    *   Classification: Accuracy, Precision, Recall (Focus on Recall for failures).
    *   Regression: RMSE (Root Mean Square Error).

---

## SLIDE 16: RESULTS & PERFORMANCE
*   **Risk Prediction:** Achieved ~85% Recall (successfully catching most failures).
*   **Delay Prediction:** High accuracy in identifying "In-Transit" delays.
*   **Observations:** Machine temperature is the strongest predictor of efficiency drops.
*   **System Latency:** Dashboard updates < 3 seconds after data ingestion.

---

## SLIDE 17: DASHBOARD & VISUALIZATION
*   **Tool:** Streamlit (Python framework).
*   **Key Features:**
    *   **Live Monitoring:** Toggles real-time data flow.
    *   **KPI Cards:** Instant view of Efficiency, Risk, and Output.
    *   **Interactive Charts:** Zoomable production timelines.
    *   **Sidebar Controls:** Filters for specific machines or suppliers.

---

## SLIDE 18: LIMITATIONS
*   **Simulated Data:** Logic is realistic but synthetic; real sensors may have more noise.
*   **Local Execution:** Currently hosted on `localhost`; needs cloud server for remote access.
*   **Basic Security:** No role-based access control (RBAC) implemented yet.

---

## SLIDE 19: FUTURE ENHANCEMENTS
*   **IoT Integration:** Connect to physical Arduino/Raspberry Pi sensors.
*   **Advanced Models:** Upgrade to LSTM (Deep Learning) for time-series forecasting.
*   **Alerting System:** SMS/Email integration via Twilio for critical risks.
*   **Dockerization:** Containerize the app for easier cloud deployment.

---

## SLIDE 20: CONCLUSION
*   **Achievement:** Successfully built an end-to-end monitoring system with predictive capabilities.
*   **Impact:** Demonstrates how AI can reduce costs and improve transparency in manufacturing.
*   **Final Thought:** The system bridges the gap between raw data and actionable intelligence.
*   **Status:** Prototype ready for pilot testing.

