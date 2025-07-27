from pydantic import BaseModel
from typing import Optional


class CounterPartySchema(BaseModel):
    id: Optional[str] = None
    alias: str
    provider_id: str
    provider_name: str
    account_number: str
    account_type: str
