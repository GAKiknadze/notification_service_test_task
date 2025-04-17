from pydantic import BaseModel, Field


class DBConfig(BaseModel):
    uri: str = Field(..., alias="uri")
