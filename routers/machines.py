from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from models.machine import Machine, CreatePodRequest, CreateTemplateRequest
from models.template import CeliumTemplateCreate, CeliumTemplateResponse
from models.pod import RentPodPayload, RentPodResponse, Pod
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

@router.post("/template", response_model=CeliumTemplateResponse)
async def create_template(request: CreateTemplateRequest):
    """
    Create a template for a machine.
    
    This endpoint:
    1. Creates a template with the provided Docker image and configuration
    2. Returns the template data for further processing
    
    Note: The template will need time to be verified before it can be used to create a pod.
    Users should implement their own logic to check for verification status.
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
    
    return template_response

@router.get("/template/{template_id}", response_model=CeliumTemplateResponse)
async def get_template_status(template_id: str):
    """
    Get the status of a template by its ID.
    
    This endpoint allows checking if a template has been verified and is ready for pod creation.
    
    The template status will progress through these stages:
    - CREATED: Initial state after creation
    - VERIFY_PENDING: Celium is verifying the template
    - VERIFY_SUCCESS: Template is verified and ready for pod creation
    - VERIFY_FAILED: Verification failed
    
    When status is VERIFY_SUCCESS, the template can be used with the create_machine endpoint.
    """
    template = await CeliumApiService.get_template(template_id)
    return template

@router.get("/{pod_id}", response_model=Pod)
async def get_pod(pod_id: str):
    """
    Get detailed information about a pod by its ID.
    
    This endpoint retrieves the current state of a pod, including:
    - Status
    - Pod name
    - GPU information
    - Template and executor IDs
    - Creation and update timestamps
    
    Note: The pod ID is the same as the executor ID that was assigned when creating the pod.
    """
    pod = await CeliumApiService.get_pod(pod_id)
    return pod

@router.post("/", response_model=RentPodResponse)
async def create_machine(request: CreatePodRequest):
    """
    Create a machine (pod) using an existing template.
    
    This endpoint:
    1. Uses an existing template ID to rent a pod on the specified executor
    2. Returns a response with the executor ID as the pod ID reference
    
    Note: The template must be in VERIFY_SUCCESS status before it can be used.
    """
    # Create pod payload
    pod_payload = RentPodPayload(
        pod_name=request.name,
        template_id=request.template_id,
        user_public_key=request.ssh_key
    )
    
    # Rent pod with the template
    pod_response = await CeliumApiService.rent_pod(request.executor_id, pod_payload)
    
    return pod_response 