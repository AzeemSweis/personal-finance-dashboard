from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class BalanceSnapshotResponse(BaseModel):
    id: int
    account_id: int
    date: date
    balance: float
    available_balance: Optional[float]
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True


class AccountBalance(BaseModel):
    account_id: int
    account_name: str
    account_type: str
    institution_name: Optional[str]
    current_balance: float
    available_balance: Optional[float]
    currency: str
    last_updated: datetime


class BalanceOverviewResponse(BaseModel):
    total_balance: float
    total_available_balance: float
    currency: str
    accounts: List[AccountBalance]
    net_worth_trend: List[Dict[str, float]]  # List of {date: balance} objects
    last_updated: datetime

    class Config:
        from_attributes = True
