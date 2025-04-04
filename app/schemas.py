from pydantic import BaseModel


class Rool(BaseModel):
    id: str
    condition: str
