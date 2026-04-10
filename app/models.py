# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from database import Base
from datetime import datetime, timezone

class Telemetry(Base):
    __tablename__ = "telemetry_readings"

    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String, index=True)
    # timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    speed = Column(Float)
    rpm = Column(Integer)
    coolant_temp = Column(Float)
    battery_voltage = Column(Float)

class AlertConfig(Base):
    __tablename__ = "alert_configurations"
    __table_args__ = (UniqueConstraint('vin', 'metric', name='uq_vin_metric'),)
    
    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String, index=True)
    metric = Column(String)
    threshold = Column(Float)