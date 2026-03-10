"""
Retrain and re-save all ML models using the current sklearn version.
Run this once to eliminate InconsistentVersionWarning on model load.
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

np.random.seed(42)
N = 2000

# ── PRODUCTION RISK DATASET ──────────────────────────────────────────────────
machine_ids = ['M1', 'M2', 'M3']
le_machine = LabelEncoder().fit(machine_ids)

speed_rpm      = np.random.uniform(700, 1000, N)
temperature_c  = np.random.uniform(28, 42, N)
downtime_min   = np.random.exponential(1.2, N)
target_output  = np.random.randint(80, 150, N)
machine_id_raw = np.random.choice(machine_ids, N)
machine_enc    = le_machine.transform(machine_id_raw)

# label: risk when thermal stress is high or downtime > 2 min
thermal_stress = (temperature_c - 30) * (speed_rpm / 1000)
at_risk = ((thermal_stress > 5) | (downtime_min > 2.0)).astype(int)

# Use DataFrame to keep feature names
X_prod = pd.DataFrame({
    'speed_rpm': speed_rpm,
    'downtime_minutes': downtime_min,
    'temperature_c': temperature_c,
    'target_output': target_output,
    'machine_id_encoded': machine_enc
})

rf_prod = RandomForestClassifier(n_estimators=200, max_depth=10,
                                  class_weight='balanced', random_state=42)
rf_prod.fit(X_prod, at_risk)
joblib.dump(rf_prod, os.path.join(MODELS_DIR, 'production_risk_rf_model.pkl'))
joblib.dump(le_machine, os.path.join(MODELS_DIR, 'le_machine_id.pkl'))
print("  [OK] production_risk_rf_model.pkl  +  le_machine_id.pkl")

# ── SUPPLIER DELAY DATASET ───────────────────────────────────────────────────
supplier_ids   = ['S1', 'S2', 'S3']
material_types = ['Cotton', 'Yarn', 'Dyes']
trans_statuses = ["in-transit", "delayed", "arrived"]

le_sup  = LabelEncoder().fit(supplier_ids)
le_mat  = LabelEncoder().fit(material_types)
le_trans = LabelEncoder().fit(trans_statuses)

sup_id_raw   = np.random.choice(supplier_ids,   N)
mat_raw      = np.random.choice(material_types, N)
trans_raw    = np.random.choice(trans_statuses, N)
order_qty    = np.random.randint(50, 500, N)
price_per_kg = np.random.uniform(2.0, 15.0, N)

sup_enc   = le_sup.transform(sup_id_raw)
mat_enc   = le_mat.transform(mat_raw)
trans_enc = le_trans.transform(trans_raw)

# delayed if status is 'delayed' or order_qty > 350
delayed = ((trans_raw == 'delayed') | (order_qty > 350)).astype(int)

# Use DataFrame to keep feature names
X_sup = pd.DataFrame({
    'supplier_id_encoded': sup_enc,
    'material_type_encoded': mat_enc,
    'order_quantity': order_qty,
    'price_per_kg': price_per_kg,
    'transportation_status_encoded': trans_enc
})

rf_sup = RandomForestClassifier(n_estimators=200, max_depth=10,
                                 class_weight='balanced', random_state=42)
rf_sup.fit(X_sup, delayed)
joblib.dump(rf_sup, os.path.join(MODELS_DIR, 'supplier_delay_rf_model.pkl'))
joblib.dump(le_sup,   os.path.join(MODELS_DIR, 'le_supplier_id.pkl'))
joblib.dump(le_mat,   os.path.join(MODELS_DIR, 'le_material_type.pkl'))
joblib.dump(le_trans, os.path.join(MODELS_DIR, 'le_transportation_status.pkl'))
print("  [OK] supplier_delay_rf_model.pkl  +  encoders")

# ── EFFICIENCY DATASET ───────────────────────────────────────────────────────
actual_output = target_output * (0.7 + 0.35 * np.random.rand(N))
actual_output -= downtime_min * 3
efficiency = np.clip((actual_output / target_output) * 100, 40, 120)

X_eff = np.column_stack([speed_rpm, downtime_min, temperature_c, target_output])
lr_eff = LinearRegression()
lr_eff.fit(X_eff, efficiency)
joblib.dump(lr_eff, os.path.join(MODELS_DIR, 'efficiency_lr_model.pkl'))
print("  [OK] efficiency_lr_model.pkl")

print("\n[DONE] All models retrained and saved with sklearn", end=" ")
import sklearn; print(sklearn.__version__)
