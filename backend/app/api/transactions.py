from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.jwt import get_current_active_user
from ..database import get_db
from ..models.account import Account
from ..models.transaction import Transaction
from ..models.user import User
from ..schemas.transaction import (TransactionCreate, TransactionResponse,
                                   TransactionUpdate)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    category: Optional[str] = Query(None, description="Filter by transaction category"),
    limit: int = Query(100, le=1000, description="Number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get transactions for the current user with optional filters"""
    # Build query to get transactions for user's accounts
    query = select(Transaction).join(Account).where(Account.user_id == current_user.id)

    # Apply filters
    if account_id:
        query = query.where(Account.id == account_id)

    if start_date:
        query = query.where(Transaction.date >= start_date)

    if end_date:
        query = query.where(Transaction.date <= end_date)

    if category:
        query = query.where(Transaction.category == category)

    # Apply pagination and ordering
    query = query.order_by(Transaction.date.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    transactions = result.scalars().all()

    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific transaction by ID"""
    result = await db.execute(
        select(Transaction)
        .join(Account)
        .where(Transaction.id == transaction_id, Account.user_id == current_user.id)
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    return transaction


@router.post(
    "/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new transaction"""
    # Verify the account belongs to the user
    result = await db.execute(
        select(Account).where(
            Account.id == transaction_data.account_id,
            Account.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    db_transaction = Transaction(
        account_id=transaction_data.account_id,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        date=transaction_data.date,
        description=transaction_data.description,
        merchant_name=transaction_data.merchant_name,
        category=transaction_data.category,
        subcategory=transaction_data.subcategory,
        is_pending=transaction_data.is_pending,
        is_recurring=transaction_data.is_recurring,
        check_number=transaction_data.check_number,
        payment_channel=transaction_data.payment_channel,
        plaid_transaction_id=transaction_data.plaid_transaction_id,
        meta_data=transaction_data.meta_data,
    )

    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)

    return db_transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing transaction"""
    result = await db.execute(
        select(Transaction)
        .join(Account)
        .where(Transaction.id == transaction_id, Account.user_id == current_user.id)
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    # Update only provided fields
    update_data = transaction_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    await db.commit()
    await db.refresh(transaction)

    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a transaction"""
    result = await db.execute(
        select(Transaction)
        .join(Account)
        .where(Transaction.id == transaction_id, Account.user_id == current_user.id)
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    await db.delete(transaction)
    await db.commit()

    return None
