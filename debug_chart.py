import pandas as pd
from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY
import sys

# Force UTF-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def debug_data():
    print("--- DEBUG START ---")
    try:
        response = supabase.table("production_data").select("*").order("timestamp", desc=True).limit(1000).execute()
        data = response.data
        if not data:
            print("No data.")
            return

        df = pd.DataFrame(data)
        print(f"Shape: {df.shape}")
        
        # Check timestamps
        print("\nRaw Timestamps (Head):")
        print(df['timestamp'].head().to_list())
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print(f"\nMin Time: {df['timestamp'].min()}")
        print(f"Max Time: {df['timestamp'].max()}")
        
        # Check machine IDs
        print(f"\nMachine IDs: {df['machine_id'].unique()}")
        
        # Simulation of dashboard logic
        df = df.sort_values('timestamp')
        chart_df = df.groupby('machine_id').tail(20).reset_index(drop=True)
        
        print("\nChart Data Sample:")
        print(chart_df[['timestamp', 'machine_id', 'actual_output']].to_string())
        
    except Exception as e:
        print(f"Error: {e}")
    print("--- DEBUG END ---")

if __name__ == "__main__":
    debug_data()
