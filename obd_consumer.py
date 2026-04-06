import time
import json
import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "vehicle/+/telemetry"

vehicle_state = {}

def on_connect(client, userdata, flags, rc):
    """Fires when the client connects to the broker."""
    if rc == 0:
        print(f"Connected successfully! Subscribing to wildcard topic: {TOPIC}")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Fires silently in the background every time a message arrives."""
    try:
        topic_parts = msg.topic.split('/')
        vin = topic_parts[1]
        
        payload = json.loads(msg.payload.decode('utf-8'))
        vehicle_state[vin] = payload
        
    except Exception as e:
        print(f"Error processing message: {e}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting to broker...")
    client.connect(BROKER, PORT, 60)


    client.loop_start()

    try:
        while True:
            time.sleep(5)
            
            print("\n" + "="*40)
            print("       FLEET TELEMETRY SUMMARY")
            print("="*40)
            
            if not vehicle_state:
                print("No data received yet. Waiting for vehicles...")
            else:
                for vin, data in vehicle_state.items():
                    print(f"VIN: {vin}")
                    print(f"  Speed: {data.get('speed', 'N/A')} km/h")
                    print(f"  RPM:   {data.get('rpm', 'N/A')}")
                    print(f"  Temp:  {data.get('coolant_temp', 'N/A')} °C")
                    print(f"  Batt:  {data.get('battery_voltage', 'N/A')} V")
                    print("-" * 40)
                    
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
        client.loop_stop()
        client.disconnect()