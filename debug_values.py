from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY
import pandas as pd

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table("production_data").select("machine_id, actual_output, timestamp").order("timestamp", desc=True).limit(20).execute()
    data = response.data
    
    df = pd.DataFrame(data)
    print(df)
    
except Exception as e:
    print(f"Error: {e}")
