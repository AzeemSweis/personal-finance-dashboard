from sqlalchemy import (Boolean, Column, Float, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship

from .base import Base


class Portfolio(Base):
    """Portfolio model for managing investment portfolios"""

    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    total_value = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    target_allocation = Column(
        Text, nullable=True
    )  # JSON string for target asset allocation
    meta_data = Column(Text, nullable=True)  # JSON string for additional portfolio data

    # Relationships
    user = relationship("User", back_populates="portfolios")
    items = relationship(
        "PortfolioItem", back_populates="portfolio", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}', total_value={self.total_value})>"


class PortfolioItem(Base):
    """PortfolioItem model for individual investments within a portfolio"""

    __tablename__ = "portfolio_items"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    investment_id = Column(Integer, ForeignKey("investments.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    unrealized_gain_loss = Column(Float, default=0.0, nullable=False)
    unrealized_gain_loss_percent = Column(Float, default=0.0, nullable=False)
    target_allocation = Column(Float, nullable=True)  # Target percentage in portfolio
    meta_data = Column(Text, nullable=True)  # JSON string for additional item data

    # Relationships
    portfolio = relationship("Portfolio", back_populates="items")
    investment = relationship("Investment", back_populates="portfolio_items")

    def __repr__(self):
        return f"<PortfolioItem(id={self.id}, quantity={self.quantity}, current_value={self.current_value})>"
