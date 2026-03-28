"""Pydantic schemas for request/response validation."""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ExtractionMode(str, Enum):
    receipt = "receipt"
    id_card = "id_card"
    table = "table"
    generic = "generic"


class ExtractionResult(BaseModel):
    mode: ExtractionMode
    filename: str
    raw_text: str
    structured: Dict[str, Any]
    confidence: Optional[str] = None
    model_used: str


class ReceiptData(BaseModel):
    merchant: Optional[str] = None
    date: Optional[str] = None
    items: List[Dict[str, Any]] = []
    subtotal: Optional[str] = None
    tax: Optional[str] = None
    total: Optional[str] = None
    payment_method: Optional[str] = None


class IDCardData(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    id_number: Optional[str] = None
    expiry: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None


class TableData(BaseModel):
    headers: List[str] = []
    rows: List[List[str]] = []
