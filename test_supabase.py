# test_supabase.py
from supabase import create_client
import os, sys

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL or SUPABASE_KEY not set in environment.")
    sys.exit(1)

print("Using SUPABASE_URL:", SUPABASE_URL)
# Keep key hidden except first/last 4 for verification
print("SUPABASE_KEY preview:", SUPABASE_KEY[:4] + "..." + SUPABASE_KEY[-4:])

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Try a harmless read
    resp = supabase.table("production_data").select("*").limit(1).execute()
    print("Status:", resp.status_code if hasattr(resp, 'status_code') else "ok")
    print("Data sample:", resp.data)
except Exception as e:
    print("Connection test failed:", type(e).__name__, e)

