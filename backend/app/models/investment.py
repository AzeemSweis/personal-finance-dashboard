import enum

from sqlalchemy import Boolean, Column, Date, Enum, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class InvestmentType(enum.Enum):
    """Enumeration for investment types"""

    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"
    OPTION = "option"
    FUTURE = "future"
    CRYPTO = "crypto"
    COMMODITY = "commodity"
    REAL_ESTATE = "real_estate"
    OTHER = "other"


class Investment(Base):
    """Investment model for tracking individual investment securities"""

    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(InvestmentType), nullable=False)
    exchange = Column(String(20), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    current_price = Column(Float, nullable=True)
    price_date = Column(Date, nullable=True)
    market_cap = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    expense_ratio = Column(Float, nullable=True)  # For ETFs and mutual funds
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    meta_data = Column(
        Text, nullable=True
    )  # JSON string for additional investment data

    # Relationships
    portfolio_items = relationship("PortfolioItem", back_populates="investment")

    def __repr__(self):
        return f"<Investment(id={self.id}, symbol='{self.symbol}', name='{self.name}', type={self.type.value})>"
