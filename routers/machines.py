from fastapi import APIRouter, HTTPException
from typing import List
from models.machine import Machine, CreateMachineRequest
from models.template import CeliumTemplateCreate
from models.pod import RentPodPayload, RentPodResponse
from services.celium_api import CeliumApiService

router = APIRouter(
    prefix="/machines",
    tags=["machines"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[Machine])
async def get_machines():
    """
    Get all machines from the Celium API.
    """
    machines = await CeliumApiService.get_executors()
    return machines 

@router.post("/", response_model=RentPodResponse)
async def create_machine(request: CreateMachineRequest):
    """
    Create a machine using template and pod rental on Celium API.
    
    This endpoint:
    1. Creates a template with the provided Docker image and configuration
    2. Rents a pod on the specified executor using the created template
    """
    # Create template
    template_data = CeliumTemplateCreate(
        docker_image=request.docker_image,
        docker_image_digest=request.docker_image_digest,
        docker_image_tag=request.docker_image_tag,
        startup_commands=request.startup_commands,
        internal_ports=request.port_mapping
    )
    
    template_response = await CeliumApiService.create_template(template_data)
    
    # Rent pod with the created template
    pod_payload = RentPodPayload(
        pod_name=request.name,
        template_id=template_response.id,
        user_public_key=request.ssh_key
    )
    
    pod_response = await CeliumApiService.rent_pod(request.executor_id, pod_payload)
    
    return pod_response 