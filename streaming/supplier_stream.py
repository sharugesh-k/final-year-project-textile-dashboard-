from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY
import random, time
from datetime import datetime, timedelta

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

suppliers = ["S1", "S2", "S3"]
materials = ["Cotton", "Yarn", "Dyes"]
status_options = ["in-transit", "delayed", "arrived"]

def generate_supplier_record():
    supplier = random.choice(suppliers)
    material = random.choice(materials)
    expected_date = datetime.utcnow() + timedelta(days=random.randint(2, 10))
    actual_date = expected_date + timedelta(days=random.randint(-1, 5))
    order_qty = random.randint(500, 2000)
    received_qty = order_qty - random.randint(0, 200)
    price = round(random.uniform(120, 200), 2)
    status = random.choice(status_options)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "supplier_id": supplier,
        "material_type": material,
        "expected_delivery_date": expected_date.strftime("%Y-%m-%d"),
        "actual_delivery_date": actual_date.strftime("%Y-%m-%d"),
        "order_quantity": order_qty,
        "received_quantity": received_qty,
        "price_per_kg": price,
        "transportation_status": status
    }

def start_streaming(interval_seconds: int = 8):
    print("Streaming supplier data to Supabase... (press Ctrl+C to stop)\n")
    try:
        while True:
            record = generate_supplier_record()
            supabase.table("supplier_data").insert(record).execute()
            print("Inserted:", record)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nStopped supplier stream by user.")

if __name__ == '__main__':
    start_streaming()
