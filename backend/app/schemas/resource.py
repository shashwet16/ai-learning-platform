import uuid

from pydantic import BaseModel, ConfigDict


class ResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lesson_id: uuid.UUID
    title: str
    url: str
    description: str
    resource_type: str
    order: int
