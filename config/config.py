import os

# Use environment variables for secrets. Edit .env or set these in your shell.
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jjfgcomlvfnwuiurtzkd.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqZmdjb21sdmZud3VpdXJ0emtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3MjgwNDEsImV4cCI6MjA4MDMwNDA0MX0.SI6kTX6Xo3s1kLa8sAVBBkDFsZBCALAFMfQX6A6_9hU")

def get_supabase_client(create_client):
    """Helper to create a supabase client using the configured URL & KEY."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)
