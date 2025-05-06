import httpx
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.machine import Machine
from models.template import CeliumTemplateCreate, CeliumTemplateResponse
from models.pod import RentPodPayload, RentPodResponse, Pod, TemplateInfo

class CeliumApiService:
    BASE_URL: str = "https://celiumcompute.ai/api"
    
    @classmethod
    def _get_headers(cls) -> Dict[str, str]:
        """Get common headers for all API requests, including the API key."""
        api_key = os.environ.get("CELIUM_API_KEY")
        if not api_key:
            raise ValueError("CELIUM_API_KEY environment variable is not set")
        
        return {
            "X-API-KEY": api_key
        }
    
    @classmethod
    async def get_executors(cls) -> List[Machine]:
        """
        Fetch executor data from Celium API and map to Machine model.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{cls.BASE_URL}/executors",
                headers=cls._get_headers()
            )
            response.raise_for_status()
            executors_data = response.json()
            
            # Use the from_celium method to map the data
            return [Machine.from_celium(executor) for executor in executors_data]
    
    @classmethod        
    async def create_template(cls, template_data: CeliumTemplateCreate) -> CeliumTemplateResponse:
        """
        Create a new template in Celium.
        
        :param template_data: CeliumTemplateCreate object containing template configuration
        :return: Created template data as CeliumTemplateResponse (with id and status)
        """
        url = f"{cls.BASE_URL}/templates"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=template_data.model_dump(),
                headers=cls._get_headers()
            )
            response.raise_for_status()
            
            response_data = response.json()
            return CeliumTemplateResponse(
                id=response_data.get("id"),
                status=response_data.get("status")
            )
    
    @classmethod
    async def get_template(cls, template_id: str) -> CeliumTemplateResponse:
        """
        Get the status of a template by its ID.
        
        :param template_id: ID of the template to check
        :return: Template response with status
        """
        url = f"{cls.BASE_URL}/templates/{template_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=cls._get_headers()
            )
            response.raise_for_status()
            
            response_data = response.json()
            return CeliumTemplateResponse(
                id=response_data.get("id"),
                status=response_data.get("status")
            )
            
    @classmethod
    async def get_pod(cls, pod_id: str) -> Pod:
        """
        Get a pod by its ID.
        
        :param pod_id: ID of the pod to retrieve
        :return: Pod object with detailed information
        """
        url = f"{cls.BASE_URL}/pods/{pod_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=cls._get_headers()
            )
            response.raise_for_status()
            
            pod_data = response.json()
            print(f"Raw pod data: {json.dumps(pod_data, indent=2)}")
            
            # Use the from_celium method to create the Pod object
            return Pod.from_celium(pod_data, pod_id)
            
    @classmethod
    async def rent_pod(cls, executor_id: str, payload: RentPodPayload) -> RentPodResponse:
        """
        Rent a pod on a specific executor.
        
        :param executor_id: ID of the executor to rent the pod on
        :param payload: RentPodPayload object with pod configuration
        :return: Pod response with executor_id as the id
        """
        url = f"{cls.BASE_URL}/executors/{executor_id}/rent"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload.model_dump(),
                headers=cls._get_headers()
            )
            response.raise_for_status()
            
            raw_response = response.json()
            return RentPodResponse(id=executor_id) 