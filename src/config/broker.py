from pydantic import BaseModel, Field


class BrokerConfig(BaseModel):
    uri: str = Field(..., alias="uri")
