import time
import json
import random
import paho.mqtt.client as mqtt

VIN = "TESTVIN1234567890"
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = f"vehicle/{VIN}/telemetry"

state = {
    "speed": 0,
    "rpm": 800,
    "coolant_temp": 70,
    "battery_voltage": 12.6,
    "drive_mode": "accelerating"
}

def get_simulated_readings(state):
    # Transition drive mode randomly
    mode_roll = random.random()
    if state["drive_mode"] == "accelerating":
        if state["speed"] >= 100 or mode_roll < 0.1:
            state["drive_mode"] = "cruising"
        speed_delta = random.randint(2, 8)

    elif state["drive_mode"] == "cruising":
        if mode_roll < 0.15:
            state["drive_mode"] = "braking"
        elif mode_roll > 0.85:
            state["drive_mode"] = "accelerating"
        speed_delta = random.randint(-2, 2)

    elif state["drive_mode"] == "braking":
        if state["speed"] <= 0 or mode_roll < 0.1:
            state["drive_mode"] = "accelerating"
        speed_delta = random.randint(-10, -3)

    state["speed"] = max(0, min(130, state["speed"] + speed_delta))
    state["rpm"] = max(800, min(6000, state["speed"] * 42 + random.randint(-150, 150)))
    state["coolant_temp"] = max(70, min(105, state["coolant_temp"] + random.choice([-1, 0, 0, 0, 1])))
    state["battery_voltage"] = round(
        max(12.0, min(14.5, state["battery_voltage"] + random.uniform(-0.05, 0.05))), 1
    )

    return {k: v for k, v in state.items() if k != "drive_mode"}
    
client = mqtt.Client()

print(f"Connecting to broker: {BROKER}...")
client.connect(BROKER, PORT, 60)

if __name__ == "__main__":
    print(f"Starting OBD-II Simulator for VIN: {VIN}")
    print(f"Publishing to broker: {BROKER} on topic: {TOPIC}")
    
    try:
        while True:
            raw_data = get_simulated_readings(state)
            payload = json.dumps(raw_data)
            client.publish(TOPIC, payload)

            print(f"Published: {payload}")
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")
        client.disconnect()