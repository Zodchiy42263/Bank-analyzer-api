from typing import Literal

from pydantic import BaseModel

class TransactionsQuery(BaseModel):
    period: Literal["D", "N", "M", "K", "G", "V"]
