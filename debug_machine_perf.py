import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def debug_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Fetching production data...")
    response = supabase.table("production_data").select("*").order("timestamp", desc=True).limit(200).execute()
    
    if not response.data:
        print("No data found in production_data table.")
        return
    
    df = pd.DataFrame(response.data)
    print(f"Fetched {len(df)} records.")
    
    print("\nColumns and Dtypes:")
    print(df.dtypes)
    
    print("\nFirst 5 records:")
    print(df.head())
    
    print("\nMachine ID counts:")
    print(df['machine_id'].value_counts())
    
    print("\nTimestamp range:")
    print(f"Min: {df['timestamp'].min()}")
    print(f"Max: {df['timestamp'].max()}")
    
    # Simulate the chart processing in dashboard.py
    chart_df = df.copy()
    chart_df['timestamp'] = pd.to_datetime(chart_df['timestamp'])
    chart_df = chart_df.sort_values('timestamp')
    chart_df = chart_df.groupby('machine_id').tail(20).reset_index(drop=True)
    chart_df = chart_df.sort_values('timestamp')
    
    print(f"\nProcessed Chart DF size: {len(chart_df)}")
    if not chart_df.empty:
        print("Chart DF head:")
        print(chart_df[['timestamp', 'machine_id', 'actual_output']].head())
    else:
        print("Chart DF is EMPTY after processing!")

if __name__ == "__main__":
    debug_data()
