# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class Telemetry(Base):
    __tablename__ = "telemetry_readings"

    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    speed = Column(Float)
    rpm = Column(Integer)
    coolant_temp = Column(Float)
    battery_voltage = Column(Float)

class AlertConfig(Base):
    __tablename__ = "alert_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String, index=True)
    metric = Column(String)
    threshold = Column(Float)