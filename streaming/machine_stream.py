from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY
import random, time
from datetime import datetime

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

machines = ["M1", "M2", "M3"]

def generate_machine_record():
    machine = random.choice(machines)
    target = random.randint(80, 100)
    # Causal Logic Implementation
    # 1. Higher speed = Higher risk of overheating
    # 2. Higher temp = Lower efficiency (machine slows down or has micro-stops)
    
    speed = random.randint(700, 1000)
    
    # Temperature is now partially dependent on speed
    base_temp = 28 + ((speed - 700) / 300) * 10  # higher speed -> higher base temp
    temp = round(base_temp + random.uniform(-2, 5), 2) # add variance
    
    # Downtime is higher if temp > 38 or speed > 950
    downtime_prob = 0.05
    if temp > 38: downtime_prob += 0.2
    if speed > 950: downtime_prob += 0.15
    
    downtime = 0.0
    if random.random() < downtime_prob:
        downtime = round(random.uniform(0.5, 5.0), 2)
    
    # Actual output depends on target, downtime, and thermal efficiency
    thermal_efficiency = 1.0
    if temp > 35:
        thermal_efficiency -= (temp - 35) * 0.05 # 5% drop per degree over 35
        
    speed_efficiency = 1.0
    if speed < 750:
        speed_efficiency = 0.9 # running too slow
        
    net_efficiency = thermal_efficiency * speed_efficiency
    
    # Downtime reduces output proportionally (assuming 60 min cycle)
    uptime_ratio = max(0, (60 - downtime) / 60)
    
    actual = int(target * uptime_ratio * net_efficiency * random.uniform(0.95, 1.02))
    actual = max(0, actual) # ensure non-negative

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
