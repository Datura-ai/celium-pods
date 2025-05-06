from pydantic import BaseModel

class RentPodPayload(BaseModel):
    """Payload for renting a pod on Celium."""
    pod_name: str
    template_id: str
    user_public_key: str

class RentPodResponse(BaseModel):
    """Response model for a rented pod from Celium."""
    id: str 