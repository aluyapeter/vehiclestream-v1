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
