# BlackBox (GUI)

This directory contains the Django backend server for the Blackbox. It serves as the central hub for the embedded "Blackbox" system, managing recording sessions ("Runs"), synchronizing configurations with the ESP32 via Firebase, and providing a real-time web dashboard for tracking telemetry.

## System Architecture Overview

The system consists of three main components:
1. **ESP32 Edge Device**: Logs sensor data and pushes to Firebase.
2. **Firebase Realtime Database**: Acts as the message broker between the ESP32 and Django.
3. **Django Backend**: Listens to Firebase, stores data in an SQLite database, and serves the UI.

## Features

- **Run Management**: Create and manage "Runs" representing single tracking journeys.
- **Dynamic Configuration**: Setting up a new run pushes thresholds (Temperature, Humidity, Light) directly to Firebase (`/run_config`), which the ESP32 reads.
- **Firebase Synchronization**: 
  - Toggling an active run syncs an `Active_Run` boolean flag in Firebase to start/stop the ESP32 recording.
  - A persistent background listener syncs telemetry packets from `/shipment_logs` into local Django SQL.
- **Real-time Dashboard**: Displays live sensor readings (Temperature, Humidity, Light Level, GPS Coordinates), along with charts, and aggregated violations.

## Setup & Installation

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Add your Firebase credentials:
   Place your `firebasekey.json` inside the `main/blackbox/` directory.

3. Run migrations to set up the SQLite database:
   ```bash
   cd main
   python manage.py migrate
   ```

## Running the Server

To run the application, you need to start two separate processes:

**Process 1: Django Web Server**
Provides the HTTP server for the web interface and API endpoints.
```bash
cd main
python manage.py runserver
```

**Process 2: Firebase Background Listener**
Maintains a persistent WebSocket connection to Firebase, listening to the `/shipment_logs` node. This automatically saves every telemetry packet the ESP32 pushes into the local SQLite database.
```bash
cd main
python manage.py firebase_listener
```

## Application Structure (main/blackbox)

- `models.py`: Defines the `Run` and `SensorReading` schema.
- `views.py`: Web endpoints for listing runs, displaying run details (graphs & metrics), and toggling runs.
- `firebase_utils.py`: Helper functions to push configuration and active state to Firebase.
- `management/commands/firebase_listener.py`: The background script for real-time telemetry polling.
