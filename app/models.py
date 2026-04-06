# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class Telemetry(Base):
    __tablename__ = "telemetry_readings"

    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String, index=True) # Indexed because we will query by VIN often
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    speed = Column(Float)
    rpm = Column(Integer)
    coolant_temp = Column(Float)
    battery_voltage = Column(Float)

class AlertConfig(Base):
    __tablename__ = "alert_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String, index=True)
    metric = Column(String)    # e.g., 'speed' or 'rpm'
    threshold = Column(Float)  # e.g., 120.0