import enum

from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class AccountType(enum.Enum):
    """Enumeration for different account types"""

    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"
    RETIREMENT = "retirement"
    LOAN = "loan"
    MORTGAGE = "mortgage"
    OTHER = "other"


class Account(Base):
    """Account model for managing financial accounts"""

    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plaid_account_id = Column(
        String(255), unique=True, nullable=True
    )  # Plaid's account ID
    name = Column(String(255), nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    institution_name = Column(String(255), nullable=True)
    account_number = Column(String(50), nullable=True)  # Masked account number
    current_balance = Column(Float, default=0.0, nullable=False)
    available_balance = Column(Float, default=0.0, nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    meta_data = Column(Text, nullable=True)  # JSON string for additional account data

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )
    balance_snapshots = relationship(
        "BalanceSnapshot", back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', type={self.type.value}, balance={self.current_balance})>"
