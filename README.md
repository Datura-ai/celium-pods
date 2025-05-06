# Celium Pods API

A FastAPI service for managing Celium compute resources - create templates, rent pods, and manage GPU computing resources.

## Overview

This API service provides a simplified interface to the Celium computing platform, allowing you to:

1. Create container templates from Docker images
2. Poll template status until verification is complete 
3. Rent GPU pods based on verified templates
4. Track pod status until running
5. Access pod details including SSH connection information

## Setup

### Prerequisites

- Docker and Docker Compose
- Celium API key

### Environment Variables

Create a `.env` file with your Celium API key:

```
CELIUM_API_KEY=your_celium_api_key_here
```

### Running the Service

```bash
docker compose up -d
```

The API will be available at http://localhost:8000

## API Usage

### Creating a Template

First, create a template from a Docker image:

```bash
curl -X POST http://localhost:8000/machines/template \
  -H "Content-Type: application/json" \
  -d '{
    "docker_image": "your-docker-image",
    "docker_image_tag": "latest",
    "docker_image_digest": "",
    "startup_commands": "",
    "port_mapping": [22, 8000],
    "name": "template-test-name"
  }'
```

Response:

```json
{
  "id": "template-uuid-here",
  "status": "CREATED"
}
```

### Polling Template Status

Templates need to be verified before use. Poll the template status until it's `VERIFY_SUCCESS`:

```bash
curl http://localhost:8000/machines/template/template-uuid-here
```

Response:

```json
{
  "id": "template-uuid-here",
  "status": "VERIFY_SUCCESS"
}
```

Template status progression:
- `CREATED`: Initial state
- `VERIFY_PENDING`: Verification in progress
- `VERIFY_SUCCESS`: Template verified and ready to use
- `VERIFY_FAILED`: Verification failed

### Finding Available Machines

Get a list of available machines:

```bash
curl http://localhost:8000/machines/
```

Filter for specific GPU types:

```bash
curl -s http://localhost:8000/machines/ | jq '.[] | select(.gpu_type | contains("A100"))'
```

### Renting a Pod

Once your template is verified (`VERIFY_SUCCESS`), you can rent a pod:

```bash
curl -X POST http://localhost:8000/machines/ \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "template-uuid",
    "executor_id": "sample-executor-id",
    "ssh_key": "ssh-ed25519 AAAA...",
    "name": "template-name"
  }'
```

Response:

```json
{
  "id": "pod-uuid-here"
}
```

### Polling Pod Status

Poll the pod status until it's `RUNNING`:

```bash
curl http://localhost:8000/machines/pod-uuid-here
```

Response:

```json
{
  "id": "pod-uuid-here",
  "status": "RUNNING",
  "pod_name": "my-pod-name",
  "gpu_name": "NVIDIA A100-SXM4-80GB",
  "gpu_count": "8",
  "cpu_name": "AMD EPYC 7742 64-Core Processor",
  "ram_total": 2113573012,
  "created_at": "2025-05-06T18:19:24.059809",
  "updated_at": "2025-05-06T18:19:47.997712",
  "ssh_connect_cmd": "ssh root@64.247.196.117 -p 9002",
  "ports_mapping": {
    "22": 9002,
    "8000": 9001
  },
  "template": {
    "id": "template-id",
    "name": "SN19-LLAMA",
    "description": "",
    "docker_image": "elaich/simple-vllm-launcher"
  },
  "executor_ip_address": "64.247.196.117"
}
```

Pod status progression:
- `PENDING`: Initial state
- `RUNNING`: Pod is running and ready to use
- Other states may include `FAILED`, `STOPPED`, etc.

## Complete Workflow Example

Here's a bash script example demonstrating the complete workflow:

```bash
#!/bin/bash

# 1. Create a template
TEMPLATE_RESPONSE=$(curl -s -X POST http://localhost:8000/machines/template \
  -H "Content-Type: application/json" \
  -d '{
    "docker_image": "elaich/simple-vllm-launcher",
    "docker_image_tag": "latest",
    "startup_commands": "",
    "port_mapping": [22, 8000],
    "name": "template-name"
  }')

TEMPLATE_ID=$(echo $TEMPLATE_RESPONSE | jq -r '.id')
echo "Template created with ID: $TEMPLATE_ID"

# 2. Poll template status until verified
while true; do
  TEMPLATE_STATUS=$(curl -s http://localhost:8000/machines/template/$TEMPLATE_ID | jq -r '.status')
  echo "Template status: $TEMPLATE_STATUS"
  
  if [ "$TEMPLATE_STATUS" == "VERIFY_SUCCESS" ]; then
    echo "Template verified successfully!"
    break
  elif [ "$TEMPLATE_STATUS" == "VERIFY_FAILED" ]; then
    echo "Template verification failed."
    exit 1
  fi
  
  echo "Waiting for template verification..."
  sleep 30
done

# 3. Find an A100 machine
EXECUTOR_ID=$(curl -s http://localhost:8000/machines/ | \
  jq -r '.[] | select(.gpu_type | contains("A100")) | .id' | head -n 1)
echo "Selected executor: $EXECUTOR_ID"

# 4. Rent a pod with the template
POD_RESPONSE=$(curl -s -X POST http://localhost:8000/machines/ \
  -H "Content-Type: application/json" \
  -d "{
    \"template_id\": \"$TEMPLATE_ID\",
    \"executor_id\": \"$EXECUTOR_ID\",
    \"ssh_key\": \"ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB/6vi7VtlHAbDYurbV/k70dQql4m7GcdCuBtYMCu/t8 my-key\",
    \"name\": \"my-awesome-pod\"
  }")

POD_ID=$(echo $POD_RESPONSE | jq -r '.id')
echo "Pod created with ID: $POD_ID"

# 5. Poll pod status until running
while true; do
  POD_INFO=$(curl -s http://localhost:8000/machines/$POD_ID)
  POD_STATUS=$(echo $POD_INFO | jq -r '.status')
  echo "Pod status: $POD_STATUS"
  
  if [ "$POD_STATUS" == "RUNNING" ]; then
    echo "Pod is now running!"
    SSH_CMD=$(echo $POD_INFO | jq -r '.ssh_connect_cmd')
    echo "Connect using: $SSH_CMD"
    break
  elif [ "$POD_STATUS" == "FAILED" ]; then
    echo "Pod creation failed."
    exit 1
  fi
  
  echo "Waiting for pod to start..."
  sleep 20
done

echo "Successfully created and started pod!"
```

## API Endpoints Reference

### Templates

- `POST /machines/template` - Create a new template
- `GET /machines/template/{template_id}` - Get template status

### Machines/Pods

- `GET /machines/` - List available machines
- `POST /machines/` - Rent a pod
- `GET /machines/{pod_id}` - Get pod status and details

## Additional Information

- The pod ID is the same as the executor ID assigned during pod creation
- SSH and service ports are mapped to external ports provided in the `ports_mapping` field
- Template verification can take 5-15 minutes depending on image size and complexity
