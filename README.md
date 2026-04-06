# VehicleStream: Real-Time Telematics Gateway

VehicleStream is an asynchronous, event-driven backend service designed to ingest live vehicle telemetry data (OBD-II), store it efficiently in a relational database, and expose it via a RESTful API. It features a background alerting engine that continuously monitors data streams for threshold violations.

## System Architecture

The pipeline consists of four main components:

1. **The Edge (Simulator):** A Python script generating randomised, realistic vehicle telemetry (Speed, RPM, Coolant Temp, Battery Voltage) and publishing it to an MQTT broker.
2. **The Message Broker:** A public MQTT broker (`broker.emqx.io`) handling the high-throughput pub/sub traffic.
3. **The Gateway (FastAPI):** An asynchronous web server that manages background MQTT threads to catch incoming data while simultaneously serving HTTP API requests.
4. **The Database:** A native PostgreSQL database storing time-series telemetry and alert configurations.

## Prerequisites

To run this project locally, you will need:

- **Ubuntu / WSL Environment**
- **Python 3.10+**
- **PostgreSQL 15+** (Running natively, no Docker required)

## Installation & Setup

**Clone the repository and setup the virtual environment:**

```bash
git clone https://github.com/aluyapeter/vehiclestream-v1
cd vehiclestream-v1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Configure the PostgreSQL Database:**
Ensure your local PostgreSQL service is running, then execute the following commands in the psql console to create the database and user:

```SQL

CREATE DATABASE telematics;
CREATE USER api_user WITH PASSWORD 'secret123';
GRANT ALL ON SCHEMA public TO api_user; 3. Run the Application:
Start the FastAPI server. The application will automatically connect to the MQTT broker and begin listening for telemetry.
```

```bash
cd app
uvicorn main:app --reload
```

## Start the Simulator:

In a separate terminal window, activate your virtual environment and start the OBD-II simulator to begin pushing data.

```bash
python3 obd_ii_simulator.py
```

**API Endpoints**
Once running, interactive API documentation is available at http://127.0.0.1:8000/docs.

Telemetry Queries
GET /vehicles/{vin}/latest
Fetches the single most recent telemetry reading for a specified vehicle.

GET /vehicles/{vin}/history?from={timestamp}&to={timestamp}
Retrieves a historical array of telemetry data within a specific ISO 8601 UTC time window.

Alert Configuration
POST /vehicles/{vin}/alert-config
Creates a new monitoring rule for a vehicle.
Payload Example: {"metric": "speed", "threshold": 120.0}

Background Processes
The application runs a continuous asynchronous task (threshold_scanner) that wakes up every 30 seconds. It cross-references the latest telemetry against all user-defined alert configurations in the database. If a vehicle exceeds a defined threshold (e.g., speed > 120), a critical alert is logged to the system terminal.

Built With
FastAPI - The web framework

SQLAlchemy - Database ORM

Paho-MQTT (v2.0+) - IoT Messaging protocol

PostgreSQL - Relational Database
