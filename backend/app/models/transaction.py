import enum

from sqlalchemy import (Boolean, Column, Date, Enum, Float, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship

from .base import Base


class TransactionCategory(enum.Enum):
    """Enumeration for transaction categories"""

    FOOD_AND_DRINK = "food_and_drink"
    SHOPPING = "shopping"
    TRANSPORTATION = "transportation"
    TRAVEL = "travel"
    ENTERTAINMENT = "entertainment"
    HEALTH_AND_FITNESS = "health_and_fitness"
    HOME_IMPROVEMENT = "home_improvement"
    PERSONAL_CARE = "personal_care"
    EDUCATION = "education"
    BUSINESS_SERVICES = "business_services"
    GOVERNMENT_SERVICES = "government_services"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    INCOME = "income"
    INVESTMENT = "investment"
    OTHER = "other"


class Transaction(Base):
    """Transaction model for tracking financial transactions"""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    plaid_transaction_id = Column(
        String(255), unique=True, nullable=True
    )  # Plaid's transaction ID
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String(500), nullable=False)
    merchant_name = Column(String(255), nullable=True)
    category: "Column[TransactionCategory]" = Column(
        Enum(TransactionCategory), nullable=True
    )
    subcategory = Column(String(100), nullable=True)
    is_pending = Column(Boolean, default=False, nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)
    check_number = Column(String(50), nullable=True)
    payment_channel = Column(String(50), nullable=True)  # online, in store, other
    meta_data = Column(
        Text, nullable=True
    )  # JSON string for additional transaction data

    # Relationships
    account = relationship("Account", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, description='{self.description}', date={self.date})>"
