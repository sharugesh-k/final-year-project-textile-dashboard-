import pandas as pd
import streamlit as st
import json
import os
from datetime import datetime
from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY

# Local mock database path
MOCK_DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mock_db.json')

class DataProcessor:
    def __init__(self):
        # Initialize mock state in session_state if not present
        if 'use_mock_mode' not in st.session_state:
            st.session_state['use_mock_mode'] = False
            
        self.supabase = self._init_connection()
        
        # If connection failed once, stay in mock mode for this session
        if self.supabase is None:
            st.session_state['use_mock_mode'] = True
            
        self.use_mock = st.session_state['use_mock_mode']
        
        if self.use_mock:
            st.sidebar.warning("🛡️ Running in Local Mock Mode")

    @st.cache_resource
    def _init_connection(_self):
        """Initialize Supabase connection with caching."""
        try:
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            # Minimal health check: can we reach the domain?
            # If getaddrinfo failed before, this will fail fast.
            return client
        except Exception:
            return None

    def fetch_data(self):
        """Fetch production and supplier data from Supabase or Local Mock."""
        if not self.use_mock:
            try:
                prod_response = self.supabase.table("production_data")\
                    .select("*").order("timestamp", desc=True).limit(200).execute()
                
                sup_response = self.supabase.table("supplier_data")\
                    .select("*").order("timestamp", desc=True).limit(100).execute()
                
                prod_df = pd.DataFrame(prod_response.data) if prod_response.data else pd.DataFrame()
                sup_df = pd.DataFrame(sup_response.data) if sup_response.data else pd.DataFrame()
                
                return self._process_production_data(prod_df), self._process_supplier_data(sup_df)
            except Exception as e:
                st.session_state['use_mock_mode'] = True
                self.use_mock = True
                st.sidebar.error(f"Connection lost: {e}")
        
        # Fallback to Mock Data
        return self._fetch_mock_data()

    def _fetch_mock_data(self):
        """Read data from local mock_db.json."""
        if os.path.exists(MOCK_DB_PATH):
            try:
                with open(MOCK_DB_PATH, 'r') as f:
                    data = json.load(f)
                prod_df = pd.DataFrame(data.get('production_data', []))
                sup_df = pd.DataFrame(data.get('supplier_data', []))
                return self._process_production_data(prod_df), self._process_supplier_data(sup_df)
            except Exception as e:
                st.error(f"Error reading mock file: {e}")
        return pd.DataFrame(), pd.DataFrame()

    def get_total_output(self):
        """Calculate the total cumulative output."""
        if not self.use_mock:
            try:
                total = 0
                page_size = 1000
                offset = 0
                while True:
                    response = self.supabase.table("production_data")\
                        .select("actual_output")\
                        .range(offset, offset + page_size - 1)\
                        .execute()
                    if not response.data: break
                    total += sum(pd.to_numeric(item.get('actual_output', 0), errors='coerce') or 0 for item in response.data)
                    if len(response.data) < page_size: break
                    offset += page_size
                    if offset > 100000: break
                return int(total)
            except Exception as e:
                print(f"Supabase Total Error: {e}")
                st.session_state['use_mock_mode'] = True
                self.use_mock = True

        # Mock total output - read directly from file to be sure
        if os.path.exists(MOCK_DB_PATH):
            try:
                with open(MOCK_DB_PATH, 'r') as f:
                    data = json.load(f)
                prod_list = data.get('production_data', [])
                total = 0
                for item in prod_list:
                    val = item.get('actual_output', 0)
                    try:
                        total += int(float(val))
                    except (ValueError, TypeError):
                        pass
                return total
            except Exception as e:
                print(f"Mock Total Error: {e}")
        return 0

    def _process_production_data(self, df):
        """Clean and calculate derived metrics for production data."""
        if df.empty:
            return df
        
        # Ensure numeric columns
        for col in ['actual_output', 'target_output', 'speed_rpm', 'temperature_c', 'downtime_minutes']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['output_gap'] = df['target_output'] - df['actual_output']
        # Fixed division by zero
        df['efficiency'] = (df['actual_output'] / df['target_output'].replace(0, 1) * 100).fillna(0)
        df['status'] = df['efficiency'].apply(
            lambda x: 'Critical' if x < 75 else 'Warning' if x < 90 else 'Normal'
        )
        return df

    def _process_supplier_data(self, df):
        """Clean and calculate risk metrics for supplier data."""
        if df.empty:
            return df
            
        # Ensure numeric
        if 'order_quantity' in df.columns:
            df['order_quantity'] = pd.to_numeric(df['order_quantity'], errors='coerce').fillna(0)

        df['expected_delivery_date'] = pd.to_datetime(df['expected_delivery_date'])
        df['actual_delivery_date'] = pd.to_datetime(df['actual_delivery_date'])
        df['delay_days'] = (df['actual_delivery_date'] - df['expected_delivery_date']).dt.days
        df['supply_risk'] = df['delay_days'].apply(
            lambda x: 'High Risk' if x > 2 else 'Moderate Risk' if x > 0 else 'On Time'
        )
        return df
