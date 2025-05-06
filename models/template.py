from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import uuid

def generate_default_name() -> str:
    """Generate a default name for a template with a random suffix."""
    return f"celium-pods-{uuid.uuid4().hex[:8]}"

class CeliumTemplateCreate(BaseModel):
    """Request model for creating a template in Celium."""
    category: str = "PYTORCH"
    container_start_immediately: bool = True
    description: str = ""
    docker_image: str
    docker_image_digest: str
    docker_image_tag: str
    entrypoint: str = ""
    environment: Dict[str, str] = Field(default_factory=dict)
    internal_ports: List[int] = Field(default_factory=list)
    is_private: bool = True
    name: str = Field(default_factory=generate_default_name)
    readme: str = ""
    startup_commands: str = ""
    volumes: List[str] = Field(default_factory=lambda: [""])

class CeliumTemplateResponse(BaseModel):
    """Response model for a template from Celium."""
    id: str 