from pydantic import BaseModel
from typing import Optional


class DirectDebitMetadataSchema(BaseModel):
    description: Optional[str] = ""
    reference: Optional[str] = ""


class DirectDebitSchema(BaseModel):
    source_id: str
    destination_id: str
    amount: float
    external_id: str
    registration_description: Optional[str] = ""
    checker_approval: Optional[bool] = False
    metadata: Optional[DirectDebitMetadataSchema] = None
