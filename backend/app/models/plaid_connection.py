from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class PlaidConnection(Base):
    """PlaidConnection model for managing Plaid API connections"""

    __tablename__ = "plaid_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plaid_item_id = Column(String(255), unique=True, nullable=False)  # Plaid's item ID
    access_token = Column(Text, nullable=False)  # Encrypted access token
    institution_id = Column(String(255), nullable=False)
    institution_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(
        String(50), default="pending", nullable=False
    )  # pending, success, error
    error_message = Column(Text, nullable=True)
    meta_data = Column(
        Text, nullable=True
    )  # JSON string for additional connection data

    # Relationships
    user = relationship("User", back_populates="plaid_connections")

    def __repr__(self):
        return f"<PlaidConnection(id={self.id}, institution='{self.institution_name}', status='{self.sync_status}')>"
