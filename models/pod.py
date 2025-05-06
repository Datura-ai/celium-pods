from pydantic import BaseModel
from typing import Dict, Any, Optional, ClassVar
from datetime import datetime

class RentPodPayload(BaseModel):
    """Payload for renting a pod on Celium."""
    pod_name: str
    template_id: str
    user_public_key: str

class RentPodResponse(BaseModel):
    """Response model for a rented pod from Celium."""
    id: str  # This will be populated with executor_id 

class TemplateInfo(BaseModel):
    """Nested template information within a pod response."""
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    docker_image: Optional[str] = None

class Pod(BaseModel):
    """Model representing a pod from Celium API."""
    id: str
    status: str
    pod_name: str
    gpu_name: Optional[str] = None
    gpu_count: Optional[str] = None
    cpu_name: Optional[str] = None
    ram_total: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ssh_connect_cmd: Optional[str] = None
    ports_mapping: Optional[Dict[str, int]] = None
    template: Optional[TemplateInfo] = None
    executor_ip_address: Optional[str] = None
    
    @classmethod
    def from_celium(cls, pod_data: Dict[str, Any], pod_id: str) -> "Pod":
        """
        Convert Celium API pod data to Pod model.
        
        :param pod_data: Raw pod data from Celium API
        :param pod_id: ID of the pod
        :return: Pod object with all available fields mapped
        """
        # Parse datetime strings if they exist
        created_at = pod_data.get("created_at")
        if created_at and isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                created_at = None
                
        updated_at = pod_data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                updated_at = None
        
        # Process nested template data if it exists
        template_info = None
        template_data = pod_data.get("template")
        if template_data and isinstance(template_data, dict):
            template_info = TemplateInfo(
                id=template_data.get("id"),
                name=template_data.get("name"),
                description=template_data.get("description"),
                docker_image=template_data.get("docker_image")
            )
            
        # Extract IP address from ssh_connect_cmd if available
        executor_ip_address = None
        ssh_connect_cmd = pod_data.get("ssh_connect_cmd")
        if ssh_connect_cmd and isinstance(ssh_connect_cmd, str):
            # Format is typically "ssh root@64.247.196.117 -p 9002"
            parts = ssh_connect_cmd.split("@")
            if len(parts) > 1:
                ip_part = parts[1].split(" ")[0]
                executor_ip_address = ip_part
        
        return cls(
            id=pod_id,
            status=pod_data.get("status"),
            pod_name=pod_data.get("pod_name"),
            gpu_name=pod_data.get("gpu_name"),
            gpu_count=pod_data.get("gpu_count"),
            cpu_name=pod_data.get("cpu_name"),
            ram_total=pod_data.get("ram_total"),
            created_at=created_at,
            updated_at=updated_at,
            ssh_connect_cmd=ssh_connect_cmd,
            ports_mapping=pod_data.get("ports_mapping"),
            template=template_info,
            executor_ip_address=executor_ip_address
        ) 