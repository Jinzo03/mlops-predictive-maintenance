import time
import random
import datetime
import psycopg2

# 1. Connection configuration to your Dockerized Postgres
DB_PARAMS = {
    "host": "localhost",
    "database": "smart_efuse_data",
    "user": "admin",
    "password": "password123",
    "port": "5432"
}

def setup_database():
    """Connects to the DB and creates the telemetry table if it doesn't exist."""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    # Create table schema aligning with your Smart e-Fuse features
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuse_telemetry (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            current FLOAT NOT NULL,
            voltage FLOAT NOT NULL,
            speed FLOAT NOT NULL,
            fault INT NOT NULL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Database table 'fuse_telemetry' is ready!")

def simulate_sensor_stream():
    """Simulates real-time sensor streaming into the warehouse."""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    print("Starting live sensor simulation... Press Ctrl+C to stop.")
    
    try:
        while True:
            # Generate normal operating data metrics
            current = round(random.uniform(5.0, 12.0), 2)   # Amps
            voltage = round(random.uniform(215.0, 225.0), 2) # Volts
            speed = round(random.uniform(1400.0, 1500.0), 2) # RPM
            
            # Most of the time, operation is normal (fault = 0)
            fault = 0
            
            # Introduce a rare anomaly (fault = 1) if current spikes too high
            if current > 11.5 and random.random() > 0.7:
                fault = 1
                print("⚠️ [ANOMALY DETECTED] Simulating electrical fault context!")

            current_time = datetime.datetime.now()

            # Insert data into our data warehouse
            cursor.execute(
                "INSERT INTO fuse_telemetry (timestamp, current, voltage, speed, fault) VALUES (%s, %s, %s, %s, %s)",
                (current_time, current, voltage, speed, fault)
            )
            conn.commit()
            
            print(f"[{current_time.strftime('%H:%M:%S')}] Ingested -> Current: {current}A | Voltage: {voltage}V | Speed: {speed}RPM | Fault: {fault}")
            
            # Wait 1 second before sending the next telemetry reading
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSimulation stopped safely.")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database()
    simulate_sensor_stream()