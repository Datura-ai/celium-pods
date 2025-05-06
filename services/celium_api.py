import httpx
import os
from typing import List, Dict, Any, Optional
from models.machine import Machine
from models.template import CeliumTemplateCreate, CeliumTemplateResponse
from models.pod import RentPodPayload, RentPodResponse

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
        :return: Created template data as CeliumTemplateResponse (only contains id)
        """
        url = f"{cls.BASE_URL}/templates"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=template_data.model_dump(),
                headers=cls._get_headers()
            )
            response.raise_for_status()
            
            # Extract only the id from the response
            return CeliumTemplateResponse(id=response.json().get("id"))
            
    @classmethod
    async def rent_pod(cls, executor_id: str, payload: RentPodPayload) -> RentPodResponse:
        """
        Rent a pod on a specific executor.
        
        :param executor_id: ID of the executor to rent the pod on
        :param payload: RentPodPayload object with pod configuration
        :return: RentPodResponse with the pod ID
        """
        url = f"{cls.BASE_URL}/executors/{executor_id}/rent"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload.model_dump(),
                headers=cls._get_headers()
            )
            response.raise_for_status()
            
            return RentPodResponse(id=response.json().get("id")) 