from pydantic import BaseModel
from typing import Dict, List, Optional, Any


class Machine(BaseModel):
    """Model for machine data."""
    id: str
    gpu_type: str
    gpu_count: int
    
    @classmethod
    def from_celium(cls, data: Dict[str, Any]) -> "Machine":
        """
        Create a Machine instance from Celium API executor data.
        """
        # Extract GPU details
        gpu_type = None
        if data.get("specs", {}).get("gpu", {}).get("details"):
            gpu_details = data["specs"]["gpu"]["details"][0]
            gpu_type = gpu_details.get("name")
        
        # Extract GPU count
        gpu_count = data.get("specs", {}).get("gpu", {}).get("count", 0)
        
        return cls(
            id=data.get("id"),
            gpu_type=gpu_type or "Unknown",
            gpu_count=gpu_count
        )


class CreateTemplateRequest(BaseModel):
    """Request model for creating a template, without executor and ssh details."""
    port_mapping: List[int]
    docker_image: str
    docker_image_digest: str = ""
    docker_image_tag: str = "latest"
    startup_commands: str = ""
    name: str


class CreatePodRequest(BaseModel):
    """Request model for creating a pod using an existing template."""
    template_id: str
    executor_id: str
    ssh_key: str
    name: str 
