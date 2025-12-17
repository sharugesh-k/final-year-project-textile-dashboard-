import threading
import time
import sys
import os

# Ensure we can import from the streaming directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'streaming'))

try:
    from streaming.machine_stream import start_streaming as start_machine_stream
    from streaming.supplier_stream import start_streaming as start_supplier_stream
except ImportError:
    # Fallback if running from a different context
    from machine_stream import start_streaming as start_machine_stream
    from supplier_stream import start_streaming as start_supplier_stream

def run_machine_stream():
    try:
        print("Starting Machine Stream...")
        start_machine_stream(interval_seconds=3)
    except Exception as e:
        print(f"Machine Stream Error: {e}")

def run_supplier_stream():
    try:
        print("Starting Supplier Stream...")
        start_supplier_stream(interval_seconds=5)
    except Exception as e:
        print(f"Supplier Stream Error: {e}")

if __name__ == "__main__":
    print("Initializing Manufacturing Simulation...")
    print("This script runs data streams in background threads.")
    print("Press Ctrl+C to stop all simulations.")

    t1 = threading.Thread(target=run_machine_stream, daemon=True)
    t2 = threading.Thread(target=run_supplier_stream, daemon=True)

    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        sys.exit(0)
