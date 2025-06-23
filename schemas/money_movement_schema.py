from pydantic import BaseModel, Field
from typing import Optional


class MoneyMovementMetadataSchema(BaseModel):
    description: Optional[str] = ""
    tracking_key: Optional[str] = None
    reference: Optional[str] = ""
    cep_url: Optional[str] = "https://default.cep.url"


class MoneyMovementSchema(BaseModel):
    source_id: str
    destination_id: str
    amount: float
    external_id: str
    checker_approval: Optional[bool] = False
    metadata: Optional[MoneyMovementMetadataSchema] = None
