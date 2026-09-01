from pydantic import BaseModel


class SessionRequests(BaseModel):
    account_id: int

