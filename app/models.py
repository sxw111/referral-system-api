from pydantic import BaseModel


# Pydantic models base class
class PydanticBase(BaseModel):
    class Config:
        from_attributes = True
