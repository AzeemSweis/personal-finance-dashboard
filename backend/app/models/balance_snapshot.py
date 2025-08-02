from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class BalanceSnapshot(Base):
    """BalanceSnapshot model for tracking historical account balances"""

    __tablename__ = "balance_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    balance = Column(Float, nullable=False)
    available_balance = Column(Float, nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    meta_data = Column(Text, nullable=True)  # JSON string for additional snapshot data

    # Relationships
    account = relationship("Account", back_populates="balance_snapshots")

    def __repr__(self):
        return f"<BalanceSnapshot(id={self.id}, account_id={self.account_id}, date={self.date}, balance={self.balance})>"
