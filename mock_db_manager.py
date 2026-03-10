import json
import os
from datetime import datetime

# Local mock database path
MOCK_DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mock_db.json')
MAX_RECORDS = 500

def save_mock_record(table_name, record):
    """Save a record to the local mock database atomically."""
    os.makedirs(os.path.dirname(MOCK_DB_PATH), exist_ok=True)
    
    data = {'production_data': [], 'supplier_data': []}
    if os.path.exists(MOCK_DB_PATH):
        try:
            with open(MOCK_DB_PATH, 'r') as f:
                data = json.load(f)
        except Exception:
            # If corrupted, start fresh
            pass
    
    if table_name not in data:
        data[table_name] = []
        
    # Add new record at the beginning (shift old ones)
    data[table_name].insert(0, record)
    
    # Cap size
    data[table_name] = data[table_name][:MAX_RECORDS]
    
    # Atomic write using a temp file
    temp_path = MOCK_DB_PATH + ".tmp"
    with open(temp_path, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(temp_path, MOCK_DB_PATH)

def clear_mock_db():
    """Clear the local mock database."""
    if os.path.exists(MOCK_DB_PATH):
        os.remove(MOCK_DB_PATH)
