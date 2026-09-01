from pydantic import BaseModel


class ChartsQuery(BaseModel):
    period: str
