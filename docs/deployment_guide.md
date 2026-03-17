# Krishi-Veda: Zero-Budget Deployment Guide

This guide outlines the steps to deploy the Krishi-Veda platform on low-cost edge hardware (Raspberry Pi) or cloud free-tiers.

## Environment Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Krishi-Veda-Module_v2.git
cd Krishi-Veda-Module_v2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Offline Database
```bash
# Initialize the SQLite database using the built-in engine
python3 -c "from backend.db.sqlite_engine import init_db; init_db()"
```

### 4. Start the Service
```bash
# Run the FastAPI backend using Uvicorn
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Edge Deployment (Raspberry Pi)
- Ensure Docker and Docker Compose are installed.
- Use `docker-compose up -d` to run the full stack (Backend + PWA Frontend).
