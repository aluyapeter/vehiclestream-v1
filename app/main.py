from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from paho.mqtt import client as mqtt_client
import json
import asyncio
from datetime import datetime
import models
from database import engine, SessionLocal, get_db
from pydantic import BaseModel
from typing import Literal

class AlertConfigRequest(BaseModel):
    metric: Literal["speed", "rpm", "coolant_temp", "battery_voltage"]
    threshold: float

models.Base.metadata.create_all(bind=engine)

def on_message(client, userdata, msg):
    db = SessionLocal()

    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        vin = msg.topic.split('/')[1]

        new_reading = models.Telemetry(
            vin=vin,
            speed=payload.get("speed"),
            rpm=payload.get("rpm"),
            coolant_temp=payload.get("coolant_temp"),
            battery_voltage=payload.get("battery_voltage")
        )
        db.add(new_reading)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error saving data: {e}")
    finally:
        db.close()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(" SUCCESS: FastAPI MQTT Client connected to broker.")
        client.subscribe("vehicle/+/telemetry")
        print(" Subscribed to vehicle/+/telemetry")
    else:
        print(f" ERROR: Connection failed with code {rc}")

async def threshold_scanner():
    """Runs continuously in the background, waking up every 30 seconds."""
    while True:
        await asyncio.sleep(30)
        
        db = SessionLocal()
        try:
            rules = db.query(models.AlertConfig).all()
            
            for rule in rules:
                latest_reading = db.query(models.Telemetry)\
                    .filter(models.Telemetry.vin == rule.vin)\
                    .order_by(models.Telemetry.timestamp.desc())\
                    .first()
                
                if latest_reading:
                    current_value = getattr(latest_reading, rule.metric, None) #type: ignore
                    
                    if current_value is not None and current_value > rule.threshold:
                        print("\n" + "!"*50)
                        print(f"🚨 ALERT TRIGGERED: {rule.vin}")
                        print(f"   Metric: {rule.metric.upper()}")
                        print(f"   Current Value: {current_value} (Limit: {rule.threshold})")
                        print("!"*50 + "\n")
                        
        except Exception as e:
            print(f"Scanner error: {e}")
        finally:
            db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mqtt_client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1) #type: ignore
    
    app.state.mqtt_client.on_connect = on_connect
    app.state.mqtt_client.on_message = on_message
    
    print("🚀 Attempting to connect to MQTT broker...")
    app.state.mqtt_client.connect("broker.emqx.io", 1883, 60)
    app.state.mqtt_client.loop_start()

    scanner_task = asyncio.create_task(threshold_scanner())
    
    yield
    
    print("Stopping MQTT loop...")
    app.state.mqtt_client.loop_stop()
    app.state.mqtt_client.disconnect()
    scanner_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "Telematics Gateway is running"}

@app.get("/vehicles/{vin}/latest")
def get_latest_telemetry(vin: str, db: Session = Depends(get_db)):
    """Fetches the most recent telemetry reading for a specific VIN."""

    latest_reading = db.query(models.Telemetry)\
        .filter(models.Telemetry.vin == vin)\
        .order_by(models.Telemetry.timestamp.desc())\
        .first()

    if not latest_reading:
        raise HTTPException(status_code=404, detail=f"No telemetry found for VIN: {vin}")

    return latest_reading

@app.post("/vehicles/{vin}/alert-config")
def configure_alert(vin: str, config: AlertConfigRequest, db: Session = Depends(get_db)):
    """Saves a new threshold alert configuration for a specific VIN."""
    
    new_alert = models.AlertConfig(
        vin=vin,
        metric=config.metric,
        threshold=config.threshold
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return {"status": "Alert configured successfully", "data": new_alert}

@app.get("/vehicles/{vin}/history")
def get_telemetry_history(
    vin: str,
    start_time: datetime = Query(..., alias="from"), 
    end_time: datetime = Query(..., alias="to"),
    db: Session = Depends(get_db)
):
    """Fetches all telemetry readings for a VIN within a specific time window."""
    history = db.query(models.Telemetry)\
        .filter(models.Telemetry.vin == vin)\
        .filter(models.Telemetry.timestamp >= start_time)\
        .filter(models.Telemetry.timestamp <= end_time)\
        .order_by(models.Telemetry.timestamp.desc())\
        .all()

    if not history:
        raise HTTPException(status_code=404, detail="No data found for this time window")

    return history