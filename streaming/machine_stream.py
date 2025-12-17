from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY
import random, time
from datetime import datetime

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

machines = ["M1", "M2", "M3"]

def generate_machine_record():
    machine = random.choice(machines)
    target = random.randint(80, 100)
    actual = random.randint(50, 110)
    speed = random.randint(700, 1000)
    downtime = round(random.uniform(0, 3), 2)
    temp = round(random.uniform(28, 40), 2)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "machine_id": machine,
        "target_output": target,
        "actual_output": actual,
        "speed_rpm": speed,
        "downtime_minutes": downtime,
        "temperature_c": temp
    }

def start_streaming(interval_seconds: int = 5):
    print("Streaming live machine data to Supabase... (press Ctrl+C to stop)\n")
    try:
        while True:
            record = generate_machine_record()
            supabase.table("production_data").insert(record).execute()
            print("Inserted:", record)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nStopped machine stream by user.")

if __name__ == '__main__':
    # Optional: set interval seconds by exporting ENV var MACHINE_INTERVAL or pass argument when running as module
    start_streaming()
