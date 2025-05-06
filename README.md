# Celium API

A FastAPI-based REST API for Celium Pods.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the application:
```
uvicorn main:app --reload
```

3. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

- GET `/machines` - Returns a list of machines from the Celium API

## Machine Model

Each machine has the following properties:
- `id`: Unique identifier for the machine
- `gpu_type`: Type of GPU (e.g., "NVIDIA A100")
- `gpu_count`: Number of GPUs in the machine

## External API Integration

The application integrates with the Celium API:
- Base URL: `https://celiumcompute.ai/api`
- Endpoint used: `/executors`

The service maps external machine data (executors) to the internal Machine model.
