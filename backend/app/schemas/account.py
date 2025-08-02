from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..models.account import AccountType


class AccountBase(BaseModel):
    name: str = Field(..., max_length=255)
    type: AccountType
    institution_name: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=50)
    currency: str = Field(default="USD", max_length=3)


class AccountCreate(AccountBase):
    current_balance: float = Field(default=0.0)
    available_balance: Optional[float] = None
    plaid_account_id: Optional[str] = Field(None, max_length=255)


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[AccountType] = None
    institution_name: Optional[str] = Field(None, max_length=255)
    current_balance: Optional[float] = None
    available_balance: Optional[float] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None
    meta_data: Optional[str] = None


class AccountResponse(AccountBase):
    id: int
    user_id: int
    plaid_account_id: Optional[str]
    current_balance: float
    available_balance: Optional[float]
    is_active: bool
    is_archived: bool
    meta_data: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 