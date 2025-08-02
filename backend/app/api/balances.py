from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.jwt import get_current_active_user
from ..database import get_db
from ..models.account import Account
from ..models.balance_snapshot import BalanceSnapshot
from ..models.user import User
from ..schemas.balance import (AccountBalance, BalanceOverviewResponse,
                               BalanceSnapshotResponse)

router = APIRouter(prefix="/balances", tags=["balances"])


@router.get("/overview", response_model=BalanceOverviewResponse)
async def get_balance_overview(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get balance overview for all accounts"""
    # Get all active accounts for the user
    result = await db.execute(
        select(Account).where(
            Account.user_id == current_user.id, Account.is_archived.is_(False)
        )
    )
    accounts = result.scalars().all()

    # Calculate totals
    total_balance = sum(account.current_balance for account in accounts)
    total_available_balance = sum(
        account.available_balance or account.current_balance for account in accounts
    )

    # Convert accounts to AccountBalance format
    account_balances = []
    for account in accounts:
        account_balance = AccountBalance(
            account_id=account.id,  # type: ignore
            account_name=account.name,  # type: ignore
            account_type=account.type.value,
            institution_name=account.institution_name,  # type: ignore
            current_balance=account.current_balance,  # type: ignore
            available_balance=account.available_balance,  # type: ignore
            currency=account.currency,  # type: ignore
            last_updated=account.updated_at,  # type: ignore
        )
        account_balances.append(account_balance)

    # Get net worth trend (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    trend_result = await db.execute(
        select(
            BalanceSnapshot.date,
            func.sum(BalanceSnapshot.balance).label("total_balance"),
        )
        .join(Account)
        .where(
            Account.user_id == current_user.id, BalanceSnapshot.date >= thirty_days_ago
        )
        .group_by(BalanceSnapshot.date)
        .order_by(BalanceSnapshot.date)
    )

    net_worth_trend = [
        {"date": str(row.date), "balance": float(row.total_balance)}
        for row in trend_result.all()
    ]

    return BalanceOverviewResponse(
        total_balance=total_balance,  # type: ignore
        total_available_balance=total_available_balance,  # type: ignore
        currency="USD",  # Assuming USD for now
        accounts=account_balances,
        net_worth_trend=net_worth_trend,  # type: ignore
        last_updated=datetime.utcnow(),
    )


@router.get("/snapshots", response_model=List[BalanceSnapshotResponse])
async def get_balance_snapshots(
    account_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get balance snapshots for accounts"""
    query = (
        select(BalanceSnapshot).join(Account).where(Account.user_id == current_user.id)
    )

    if account_id:
        query = query.where(Account.id == account_id)

    if start_date:
        query = query.where(BalanceSnapshot.date >= start_date)

    if end_date:
        query = query.where(BalanceSnapshot.date <= end_date)

    query = query.order_by(BalanceSnapshot.date.desc())

    result = await db.execute(query)
    snapshots = result.scalars().all()

    return snapshots


@router.get("/snapshots/{account_id}", response_model=List[BalanceSnapshotResponse])
async def get_account_balance_snapshots(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get balance snapshots for a specific account"""
    result = await db.execute(
        select(BalanceSnapshot)
        .join(Account)
        .where(Account.id == account_id, Account.user_id == current_user.id)
        .order_by(BalanceSnapshot.date.desc())
    )
    snapshots = result.scalars().all()

    if not snapshots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No balance snapshots found for this account",
        )

    return snapshots
