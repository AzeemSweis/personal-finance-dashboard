from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from ..models.transaction import TransactionCategory


class TransactionBase(BaseModel):
    amount: float = Field(..., description="Transaction amount (positive for income, negative for expenses)")
    currency: str = Field(default="USD", max_length=3)
    date: date
    description: str = Field(..., max_length=500)
    merchant_name: Optional[str] = Field(None, max_length=255)
    category: Optional[TransactionCategory] = None
    subcategory: Optional[str] = Field(None, max_length=100)
    is_pending: bool = Field(default=False)
    is_recurring: bool = Field(default=False)
    check_number: Optional[str] = Field(None, max_length=50)
    payment_channel: Optional[str] = Field(None, max_length=50)


class TransactionCreate(TransactionBase):
    account_id: int
    plaid_transaction_id: Optional[str] = Field(None, max_length=255)
    meta_data: Optional[str] = None


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = Field(None, max_length=3)
    date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=500)
    merchant_name: Optional[str] = Field(None, max_length=255)
    category: Optional[TransactionCategory] = None
    subcategory: Optional[str] = Field(None, max_length=100)
    is_pending: Optional[bool] = None
    is_recurring: Optional[bool] = None
    check_number: Optional[str] = Field(None, max_length=50)
    payment_channel: Optional[str] = Field(None, max_length=50)
    meta_data: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    account_id: int
    plaid_transaction_id: Optional[str]
    meta_data: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 