from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PortfolioBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    currency: str = Field(default="USD", max_length=3)
    is_default: bool = Field(default=False)
    target_allocation: Optional[str] = None  # JSON string


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    total_value: Optional[float] = None
    currency: Optional[str] = Field(None, max_length=3)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    target_allocation: Optional[str] = None
    meta_data: Optional[str] = None


class PortfolioResponse(PortfolioBase):
    id: int
    user_id: int
    total_value: float
    is_active: bool
    meta_data: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PortfolioItemBase(BaseModel):
    quantity: float = Field(..., gt=0)
    average_cost: float = Field(..., gt=0)
    current_value: float = Field(..., gt=0)
    unrealized_gain_loss: float = Field(default=0.0)
    unrealized_gain_loss_percent: float = Field(default=0.0)
    target_allocation: Optional[float] = Field(None, ge=0, le=100)


class PortfolioItemCreate(PortfolioItemBase):
    portfolio_id: int
    investment_id: int
    meta_data: Optional[str] = None


class PortfolioItemUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    average_cost: Optional[float] = Field(None, gt=0)
    current_value: Optional[float] = Field(None, gt=0)
    unrealized_gain_loss: Optional[float] = None
    unrealized_gain_loss_percent: Optional[float] = None
    target_allocation: Optional[float] = Field(None, ge=0, le=100)
    meta_data: Optional[str] = None


class PortfolioItemResponse(PortfolioItemBase):
    id: int
    portfolio_id: int
    investment_id: int
    meta_data: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 