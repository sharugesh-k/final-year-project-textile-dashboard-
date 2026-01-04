from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY
import pandas as pd

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Fetch same as dashboard
    response = supabase.table("production_data").select("*").order("timestamp", desc=True).limit(10).execute()
    data = response.data
    
    print(f"Fetched {len(data)} records")
    
    if len(data) > 0:
        df = pd.DataFrame(data)
        print("\nDataFrame Info:")
        print(df.info())
        print("\nFirst 5 rows:")
        print(df.head())
        
        print("\nTimestamp sample:")
        print(df['timestamp'].head())
        
        # Test conversion
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print("\nConverted Timestamps:")
        print(df['timestamp'].head())
        
        print("\nDescription:")
        print(df.describe())
    else:
        print("No data found!")

except Exception as e:
    print(f"Error: {e}")
