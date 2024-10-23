from pydantic import BaseModel


# Pydantic models base class
class PydanticBase(BaseModel):
    model_config = {
        "from_attributes": True,
    }
