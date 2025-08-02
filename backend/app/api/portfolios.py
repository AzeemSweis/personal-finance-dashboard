from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.jwt import get_current_active_user
from ..database import get_db
from ..models.investment import Investment
from ..models.portfolio import Portfolio, PortfolioItem
from ..models.user import User
from ..schemas.portfolio import (
    PortfolioCreate,
    PortfolioItemCreate,
    PortfolioItemResponse,
    PortfolioItemUpdate,
    PortfolioResponse,
    PortfolioUpdate,
)

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all portfolios for the current user"""
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.user_id == current_user.id, Portfolio.is_active.is_(True)
        )
    )
    portfolios = result.scalars().all()
    return portfolios


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific portfolio by ID"""
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    return portfolio


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new portfolio"""
    # If this is the first portfolio or marked as default, unset other defaults
    if portfolio_data.is_default:
        await db.execute(
            select(Portfolio)
            .where(Portfolio.user_id == current_user.id, Portfolio.is_default.is_(True))
            .update({Portfolio.is_default: False})
        )

    db_portfolio = Portfolio(
        user_id=current_user.id,
        name=portfolio_data.name,
        description=portfolio_data.description,
        currency=portfolio_data.currency,
        is_default=portfolio_data.is_default,
        target_allocation=portfolio_data.target_allocation,
    )

    db.add(db_portfolio)
    await db.commit()
    await db.refresh(db_portfolio)

    return db_portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing portfolio"""
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # If setting as default, unset other defaults
    if portfolio_data.is_default:
        await db.execute(
            select(Portfolio)
            .where(
                Portfolio.user_id == current_user.id,
                Portfolio.id != portfolio_id,
                Portfolio.is_default.is_(True),
            )
            .update({Portfolio.is_default: False})
        )

    # Update only provided fields
    update_data = portfolio_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio, field, value)

    await db.commit()
    await db.refresh(portfolio)

    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a portfolio (mark as inactive)"""
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    portfolio.is_active = False
    await db.commit()

    return None


# Portfolio Items endpoints
@router.get("/{portfolio_id}/items", response_model=List[PortfolioItemResponse])
async def get_portfolio_items(
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all items in a portfolio"""
    # Verify portfolio belongs to user
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    result = await db.execute(
        select(PortfolioItem).where(PortfolioItem.portfolio_id == portfolio_id)
    )
    items = result.scalars().all()

    return items


@router.post(
    "/{portfolio_id}/items",
    response_model=PortfolioItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_portfolio_item(
    portfolio_id: int,
    item_data: PortfolioItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add an item to a portfolio"""
    # Verify portfolio belongs to user
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Verify investment exists
    result = await db.execute(
        select(Investment).where(Investment.id == item_data.investment_id)
    )
    investment = result.scalar_one_or_none()

    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found"
        )

    db_item = PortfolioItem(
        portfolio_id=portfolio_id,
        investment_id=item_data.investment_id,
        quantity=item_data.quantity,
        average_cost=item_data.average_cost,
        current_value=item_data.current_value,
        unrealized_gain_loss=item_data.unrealized_gain_loss,
        unrealized_gain_loss_percent=item_data.unrealized_gain_loss_percent,
        target_allocation=item_data.target_allocation,
        meta_data=item_data.meta_data,
    )

    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)

    return db_item


@router.put("/{portfolio_id}/items/{item_id}", response_model=PortfolioItemResponse)
async def update_portfolio_item(
    portfolio_id: int,
    item_id: int,
    item_data: PortfolioItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a portfolio item"""
    # Verify portfolio belongs to user
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Get the portfolio item
    result = await db.execute(
        select(PortfolioItem).where(
            PortfolioItem.id == item_id, PortfolioItem.portfolio_id == portfolio_id
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found"
        )

    # Update only provided fields
    update_data = item_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)

    return item


@router.delete(
    "/{portfolio_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_portfolio_item(
    portfolio_id: int,
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove an item from a portfolio"""
    # Verify portfolio belongs to user
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    # Get the portfolio item
    result = await db.execute(
        select(PortfolioItem).where(
            PortfolioItem.id == item_id, PortfolioItem.portfolio_id == portfolio_id
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found"
        )

    await db.delete(item)
    await db.commit()

    return None
