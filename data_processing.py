import pandas as pd
import streamlit as st
from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY

class DataProcessor:
    def __init__(self):
        self.supabase = self._init_connection()

    @st.cache_resource
    def _init_connection(_self):
        """Initialize Supabase connection with caching."""
        try:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            st.error(f"Failed to connect to Supabase: {e}")
            return None

    def fetch_data(self):
        """Fetch production and supplier data from Supabase."""
        try:
            prod_response = self.supabase.table("production_data")\
                .select("*").order("timestamp", desc=True).limit(200).execute()
            
            sup_response = self.supabase.table("supplier_data")\
                .select("*").order("timestamp", desc=True).limit(100).execute()
            
            prod_df = pd.DataFrame(prod_response.data) if prod_response.data else pd.DataFrame()
            sup_df = pd.DataFrame(sup_response.data) if sup_response.data else pd.DataFrame()
            
            return self._process_production_data(prod_df), self._process_supplier_data(sup_df)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def _process_production_data(self, df):
        """Clean and calculate derived metrics for production data."""
        if df.empty:
            return df
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['output_gap'] = df['target_output'] - df['actual_output']
        df['efficiency'] = (df['actual_output'] / df['target_output'] * 100).fillna(0)
        
        # Categorize efficiency
        df['status'] = df['efficiency'].apply(
            lambda x: 'Critical' if x < 75 else 'Warning' if x < 90 else 'Normal'
        )
        return df

    def _process_supplier_data(self, df):
        """Clean and calculate risk metrics for supplier data."""
        if df.empty:
            return df
            
        df['expected_delivery_date'] = pd.to_datetime(df['expected_delivery_date'])
        df['actual_delivery_date'] = pd.to_datetime(df['actual_delivery_date'])
        
        # Calculate delay in days
        df['delay_days'] = (df['actual_delivery_date'] - df['expected_delivery_date']).dt.days
        df['supply_risk'] = df['delay_days'].apply(
            lambda x: 'High Risk' if x > 2 else 'Moderate Risk' if x > 0 else 'On Time'
        )
        return df
