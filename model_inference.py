"""
ML Model Inference Module
Loads and uses trained models for production risk, supplier delay, and efficiency prediction.
"""
import os
import joblib
import pandas as pd
import numpy as np

# Path to models directory
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

class MLModelManager:
    """Manager class to load and use trained ML models."""
    
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self._load_models()
    
    def _load_models(self):
        """Load all trained models and encoders."""
        try:
            # Load ML models
            self.models['production_risk'] = joblib.load(
                os.path.join(MODELS_DIR, 'production_risk_rf_model.pkl')
            )
            self.models['supplier_delay'] = joblib.load(
                os.path.join(MODELS_DIR, 'supplier_delay_rf_model.pkl')
            )
            self.models['efficiency'] = joblib.load(
                os.path.join(MODELS_DIR, 'efficiency_lr_model.pkl')
            )
            
            # Load label encoders
            self.encoders['machine_id'] = joblib.load(
                os.path.join(MODELS_DIR, 'le_machine_id.pkl')
            )
            self.encoders['supplier_id'] = joblib.load(
                os.path.join(MODELS_DIR, 'le_supplier_id.pkl')
            )
            self.encoders['material_type'] = joblib.load(
                os.path.join(MODELS_DIR, 'le_material_type.pkl')
            )
            self.encoders['transportation_status'] = joblib.load(
                os.path.join(MODELS_DIR, 'le_transportation_status.pkl')
            )
            
            print("✅ All ML models loaded successfully!")
            self.models_loaded = True
            
        except FileNotFoundError as e:
            print(f"⚠️ Model file not found: {e}")
            self.models_loaded = False
        except Exception as e:
            print(f"⚠️ Error loading models: {e}")
            self.models_loaded = False
    
    def predict_production_risk(self, df: pd.DataFrame) -> dict:
        """
        Predict production downtime risk for given production data.
        
        Args:
            df: DataFrame with columns [machine_id, speed_rpm, downtime_minutes, 
                temperature_c, target_output, actual_output]
        
        Returns:
            dict with risk_score (0-100), risk_level, and contributing_factors
        """
        if not self.models_loaded or df.empty:
            return self._fallback_production_risk(df)
        
        try:
            # Prepare features
            features = df[['speed_rpm', 'downtime_minutes', 'temperature_c', 'target_output']].copy()
            
            # Encode machine_id
            machine_encoded = self.encoders['machine_id'].transform(df['machine_id'])
            features['machine_id_encoded'] = machine_encoded
            
            # Get predictions (probability of risk)
            risk_probs = self.models['production_risk'].predict_proba(features)
            
            # Average risk probability across all records (class 1 = risk)
            if risk_probs.shape[1] > 1:
                avg_risk_score = risk_probs[:, 1].mean() * 100
            else:
                avg_risk_score = risk_probs[:, 0].mean() * 100
            
            # Determine risk level
            if avg_risk_score > 70:
                risk_level = "CRITICAL"
            elif avg_risk_score > 50:
                risk_level = "HIGH"
            elif avg_risk_score > 30:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            # Feature importance for explainability
            if hasattr(self.models['production_risk'], 'feature_importances_'):
                importances = self.models['production_risk'].feature_importances_
                feature_names = ['speed_rpm', 'downtime_minutes', 'temperature_c', 'target_output', 'machine_id']
                contributing_factors = {
                    name: f"{imp*100:.1f}% impact" 
                    for name, imp in zip(feature_names, importances)
                }
            else:
                contributing_factors = self._get_heuristic_factors(df)
            
            return {
                'risk_score': round(avg_risk_score, 1),
                'risk_level': risk_level,
                'contributing_factors': contributing_factors,
                'model_used': 'Random Forest Classifier'
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._fallback_production_risk(df)
    
    def predict_supplier_delay(self, df: pd.DataFrame) -> dict:
        """
        Predict supplier delivery delay risk.
        
        Args:
            df: DataFrame with columns [supplier_id, material_type, order_quantity, 
                price_per_kg, transportation_status]
        
        Returns:
            dict with delay_probability, risk_level, and breakdown by supplier
        """
        if not self.models_loaded or df.empty:
            return self._fallback_supplier_delay(df)
        
        try:
            # Prepare features
            features = pd.DataFrame()
            features['supplier_id_encoded'] = self.encoders['supplier_id'].transform(df['supplier_id'])
            features['material_type_encoded'] = self.encoders['material_type'].transform(df['material_type'])
            features['order_quantity'] = df['order_quantity']
            features['price_per_kg'] = df['price_per_kg']
            features['transportation_status_encoded'] = self.encoders['transportation_status'].transform(
                df['transportation_status']
            )
            
            # Get predictions
            delay_probs = self.models['supplier_delay'].predict_proba(features)
            
            # Average delay probability
            if delay_probs.shape[1] > 1:
                avg_delay_prob = delay_probs[:, 1].mean() * 100
            else:
                avg_delay_prob = delay_probs[:, 0].mean() * 100
            
            # Risk level
            if avg_delay_prob > 60:
                risk_level = "HIGH RISK"
            elif avg_delay_prob > 40:
                risk_level = "MODERATE"
            else:
                risk_level = "LOW RISK"
            
            # Per-supplier breakdown
            df_copy = df.copy()
            if delay_probs.shape[1] > 1:
                df_copy['delay_prob'] = delay_probs[:, 1] * 100
            else:
                df_copy['delay_prob'] = delay_probs[:, 0] * 100
            
            supplier_risk = df_copy.groupby('supplier_id')['delay_prob'].mean().to_dict()
            
            return {
                'delay_probability': round(avg_delay_prob, 1),
                'risk_level': risk_level,
                'supplier_breakdown': {k: f"{v:.1f}%" for k, v in supplier_risk.items()},
                'model_used': 'Random Forest Classifier'
            }
            
        except Exception as e:
            print(f"Supplier prediction error: {e}")
            return self._fallback_supplier_delay(df)
    
    def predict_efficiency(self, speed_rpm: float, downtime_minutes: float, 
                          temperature_c: float, target_output: int) -> dict:
        """
        Predict production efficiency percentage.
        
        Args:
            speed_rpm: Machine speed in RPM
            downtime_minutes: Downtime in minutes
            temperature_c: Temperature in Celsius
            target_output: Target production output
        
        Returns:
            dict with predicted_efficiency and confidence
        """
        if not self.models_loaded:
            return {'predicted_efficiency': 85.0, 'model_used': 'Fallback'}
        
        try:
            features = np.array([[speed_rpm, downtime_minutes, temperature_c, target_output]])
            predicted = self.models['efficiency'].predict(features)[0]
            
            # Clamp to realistic range
            predicted = max(min(predicted, 120), 40)
            
            return {
                'predicted_efficiency': round(predicted, 1),
                'model_used': 'Linear Regression'
            }
            
        except Exception as e:
            print(f"Efficiency prediction error: {e}")
            return {'predicted_efficiency': 85.0, 'model_used': 'Fallback'}
    
    def get_model_info(self) -> dict:
        """Get information about loaded models."""
        info = {
            'models_loaded': self.models_loaded,
            'production_risk_model': type(self.models.get('production_risk', None)).__name__,
            'supplier_delay_model': type(self.models.get('supplier_delay', None)).__name__,
            'efficiency_model': type(self.models.get('efficiency', None)).__name__,
            'encoders_loaded': list(self.encoders.keys())
        }
        return info
    
    def _fallback_production_risk(self, df: pd.DataFrame) -> dict:
        """Fallback heuristic-based risk prediction."""
        if df.empty:
            return {'risk_score': 0, 'risk_level': 'Unknown', 'contributing_factors': {}}
        
        avg_temp = df['temperature_c'].mean()
        avg_downtime = df['downtime_minutes'].mean()
        
        risk_score = 20
        if avg_temp > 35:
            risk_score += (avg_temp - 35) * 3
        if avg_downtime > 1.5:
            risk_score += avg_downtime * 10
        
        risk_score = min(max(risk_score, 0), 99)
        
        risk_level = "CRITICAL" if risk_score > 70 else "HIGH" if risk_score > 50 else "MEDIUM" if risk_score > 30 else "LOW"
        
        return {
            'risk_score': round(risk_score, 1),
            'risk_level': risk_level,
            'contributing_factors': self._get_heuristic_factors(df),
            'model_used': 'Heuristic Fallback'
        }
    
    def _fallback_supplier_delay(self, df: pd.DataFrame) -> dict:
        """Fallback supplier delay prediction."""
        if df.empty:
            return {'delay_probability': 0, 'risk_level': 'Unknown', 'supplier_breakdown': {}}
        
        delayed_count = (df['transportation_status'] == 'delayed').sum()
        total = len(df)
        delay_prob = (delayed_count / total * 100) if total > 0 else 0
        
        return {
            'delay_probability': round(delay_prob, 1),
            'risk_level': 'HIGH RISK' if delay_prob > 60 else 'MODERATE' if delay_prob > 40 else 'LOW RISK',
            'supplier_breakdown': {},
            'model_used': 'Heuristic Fallback'
        }
    
    def _get_heuristic_factors(self, df: pd.DataFrame) -> dict:
        """Get contributing factors based on heuristics."""
        avg_temp = df['temperature_c'].mean()
        avg_efficiency = (df['actual_output'] / df['target_output']).mean() * 100
        
        return {
            "Temperature Impact": f"{max(0, avg_temp - 32):.1f}°C above normal",
            "Efficiency Drop": f"{max(0, 90 - avg_efficiency):.1f}% below target",
            "Downtime Factor": f"{df['downtime_minutes'].mean():.2f} min avg"
        }


# Singleton instance for easy import
model_manager = MLModelManager()


# Legacy compatibility functions
def predict_risk(df):
    """Legacy function for backward compatibility."""
    result = model_manager.predict_production_risk(df)
    return result['risk_score'], result['risk_level'], result['contributing_factors']

def predict_supplier_risk(df):
    """Legacy function for backward compatibility."""
    result = model_manager.predict_supplier_delay(df)
    return result['delay_probability'], result['risk_level']
